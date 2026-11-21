// Deutsch lernen Plus: Stripe's notifications (webhook). Turns Plus on or off for the account.
//
//   POST .../stripe   Stripe sends events here, signed with the endpoint's secret.
//
// Events used: checkout.session.completed, customer.subscription.created/updated/deleted, invoice.paid,
// invoice.payment_failed. Whatever the event, we look up the subscription it is about, fetch its current state from
// Stripe and write that state into the profile. So a repeated, late or out-of-order event can't leave a wrong
// answer behind: the last write always reflects what Stripe says now.
//
// Secrets (Supabase dashboard -> Edge Functions -> Secrets):
//   STRIPE_WEBHOOK_SECRET   the endpoint's signing secret (whsec_...) from Stripe -> Developers -> Webhooks
//   STRIPE_SECRET_KEY       the same key the billing function uses (to fetch the subscription)
//   STRIPE_TEST_TESTERS     comma-separated account ids that may get Plus from test-mode purchases
// Turn OFF "Verify JWT" for this function: Stripe can't sign in, so it checks Stripe's signature instead.
import { createClient } from "npm:@supabase/supabase-js@2";
import { env, idOf, PAYING, periodEnd, stripe, subscriptionIdOf, testerAllowed, userHintOf, UUID, verified } from "../_shared/stripe.ts";

const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
  auth: { persistSession: false },
});
const GRACE_DAYS = 3; // Plus stays on this long past the period end, so a slightly late renewal never cuts anyone off
// Statuses after which the subscription no longer pays. "incomplete" (first payment still pending) changes nothing.
const ENDED = ["canceled", "unpaid", "incomplete_expired", "paused"];

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

async function findUserId(sub: Record<string, any>, hint?: string) {
  const { data } = await admin.from("profiles").select("user_id")
    .eq("stripe_subscription_id", String(sub.id)).limit(1).maybeSingle();
  if (data?.user_id) return data.user_id as string;
  const fromCheckout = sub.metadata?.user_id;
  if (typeof fromCheckout === "string" && UUID.test(fromCheckout)) return fromCheckout;
  if (hint) return hint;
  const customer = idOf(sub.customer);
  if (!customer) return undefined;
  const { data: byCustomer } = await admin.from("profiles").select("user_id")
    .eq("stripe_customer_id", customer).limit(1).maybeSingle();
  return byCustomer?.user_id as string | undefined;
}

async function apply(sub: Record<string, any>, hint: string | undefined, livemode: boolean) {
  const userId = await findUserId(sub, hint);
  if (!userId) {
    console.error("subscription without a known account", sub.id);
    return;
  }
  if (!testerAllowed(userId, livemode)) {
    console.error("test-mode subscription for an account that isn't a tester; ignored", sub.id);
    return;
  }
  const { data: current } = await admin.from("profiles")
    .select("stripe_subscription_id, plus_source").eq("user_id", userId).maybeSingle();
  const stored = current?.stripe_subscription_id;
  const status = String(sub.status);
  if (stored && stored !== sub.id && !PAYING.includes(status)) {
    console.error("ignoring an older subscription that ended", sub.id);
    return;
  }
  const update: Record<string, unknown> = {
    stripe_customer_id: idOf(sub.customer), stripe_subscription_id: sub.id, stripe_status: status,
    updated_at: new Date().toISOString(),
  };
  const ends = periodEnd(sub);
  if (PAYING.includes(status) && ends) {
    update.plan = "plus";
    update.plus_until = new Date(ends.getTime() + GRACE_DAYS * 86400000).toISOString();
    update.plus_source = "stripe";
  } else if (ENDED.includes(status) && current?.plus_source !== "paddle") {
    // A Paddle subscription that is still running keeps its Plus; only Stripe's own Plus ends here.
    update.plan = "free";
    update.plus_until = new Date().toISOString();
  }
  const { data: rows, error } = await admin.from("profiles").update(update).eq("user_id", userId).select("user_id");
  if (error) throw new Error(`profile update failed: ${error.message}`);
  if (!rows?.length) console.error("no profile for account", userId);
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return json({ error: "not found" }, 404);
  const raw = await req.text();
  const secret = env("STRIPE_WEBHOOK_SECRET");
  if (!secret) console.error("STRIPE_WEBHOOK_SECRET is not set");
  if (!(await verified(req.headers.get("stripe-signature") ?? "", raw, secret))) {
    console.error("webhook signature check failed");
    return json({ error: "bad signature" }, 400);
  }
  const event = JSON.parse(raw);
  const subId = subscriptionIdOf(event);
  if (!subId) return json({ ok: true, ignored: event.type });
  const r = await stripe("GET", `/subscriptions/${encodeURIComponent(subId)}`);
  if (!r.ok) {
    if (r.status === 404) {
      console.error("subscription not found", subId);
      return json({ ok: true });
    }
    // Stripe retries failed deliveries for up to three days, so a hiccup here is safe.
    console.error("couldn't fetch the subscription", r.status, JSON.stringify(r.data).slice(0, 300));
    return json({ error: "try again" }, 500);
  }
  try {
    await apply(r.data, userHintOf(event), Boolean(r.data.livemode ?? event.livemode));
  } catch (e) {
    console.error(String(e));
    return json({ error: "try again" }, 500);
  }
  return json({ ok: true });
});
