// Deutsch lernen Plus: buying and managing Plus with Stripe (Stripe Managed Payments, Stripe as merchant of record).
// The app calls these with the signed-in user's Supabase token:
//
//   POST .../billing/checkout {plan: "monthly"|"yearly"}  -> {url} of a Stripe Checkout page for this account
//   POST .../billing/portal                               -> {url} of Stripe's "manage subscription" page
//   POST .../billing/cancel                               -> cancels the subscription now (used before deleting an account)
//
// Plus itself is switched on and off by the stripe function (the webhook), never here.
//
// Secrets (Supabase dashboard -> Edge Functions -> Secrets):
//   STRIPE_SECRET_KEY      sk_test_... while testing, sk_live_... (or a restricted rk_ key) for real payments
//   STRIPE_PRICE_MONTHLY   price id of the monthly price (price_...)
//   STRIPE_PRICE_YEARLY    price id of the yearly price
//   STRIPE_SUCCESS_URL     page shown after paying (e.g. https://deutschlernenapp.com/checkout/done/)
//   STRIPE_CANCEL_URL      page shown when the buyer goes back without paying
// "Verify JWT" can stay on for this function: only signed-in users call it. It checks the token itself as well.
import { createClient } from "npm:@supabase/supabase-js@2";
import { env, PAYING, stripe } from "../_shared/stripe.ts";

const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
  auth: { persistSession: false },
});

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

// Same check as the ai function: the token must belong to a real, signed-in user.
async function signedInUser(req: Request) {
  const token = (req.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "");
  if (!token) return null;
  const { data, error } = await admin.auth.getUser(token);
  return error ? null : data?.user ?? null;
}

async function profileOf(userId: string) {
  const { data } = await admin.from("profiles")
    .select("plan, plus_until, plus_source, stripe_customer_id, stripe_subscription_id, stripe_status")
    .eq("user_id", userId).maybeSingle();
  return data ?? {};
}

async function checkout(req: Request, user: { id: string; email?: string }) {
  const body = await req.json().catch(() => ({}));
  const plan = body?.plan === "monthly" ? "monthly" : "yearly";
  const price = env(plan === "monthly" ? "STRIPE_PRICE_MONTHLY" : "STRIPE_PRICE_YEARLY");
  const success = env("STRIPE_SUCCESS_URL"), cancel = env("STRIPE_CANCEL_URL");
  if (!env("STRIPE_SECRET_KEY") || !price || !success) {
    console.error("billing isn't configured: set STRIPE_SECRET_KEY, STRIPE_PRICE_MONTHLY/YEARLY and STRIPE_SUCCESS_URL");
    return json({ error: "Checkout isn't available yet. Try again later." }, 503);
  }
  const profile: Record<string, any> = await profileOf(user.id);
  // No second subscription by accident: someone who already pays manages their plan instead.
  if (profile.stripe_subscription_id && PAYING.includes(profile.stripe_status)) {
    return json({ error: "You already have Plus. Use Manage subscription to change or cancel it." }, 409);
  }
  const session: Record<string, unknown> = {
    mode: "subscription",
    line_items: [{ price, quantity: 1 }],
    managed_payments: { enabled: true },  // Stripe sells as merchant of record and handles sales tax and VAT
    client_reference_id: user.id,
    metadata: { user_id: user.id },
    subscription_data: { metadata: { user_id: user.id } },
    success_url: success,
    cancel_url: cancel || undefined,
  };
  // A returning buyer keeps one Stripe customer (one payment history, one portal); a new one gets the email prefilled.
  if (profile.stripe_customer_id) session.customer = profile.stripe_customer_id;
  else if (user.email) session.customer_email = user.email;
  const r = await stripe("POST", "/checkout/sessions", session);
  if (!r.ok || !r.data.url) {
    console.error("checkout session failed", r.status, JSON.stringify(r.data).slice(0, 500));
    return json({ error: "Couldn't open checkout. Try again later." }, 502);
  }
  return json({ url: r.data.url });
}

async function portal(user: { id: string }) {
  const profile: Record<string, any> = await profileOf(user.id);
  if (!profile.stripe_customer_id) return json({ error: "There's no subscription on this account yet." }, 404);
  const r = await stripe("POST", "/billing_portal/sessions", {
    customer: profile.stripe_customer_id,
    return_url: env("STRIPE_PORTAL_RETURN_URL") || env("STRIPE_SUCCESS_URL") || undefined,
  });
  if (!r.ok || !r.data.url) {
    console.error("portal session failed", r.status, JSON.stringify(r.data).slice(0, 500));
    return json({ error: "Couldn't open subscription settings. Try again later." }, 502);
  }
  return json({ url: r.data.url });
}

async function cancel(user: { id: string }) {
  const profile: Record<string, any> = await profileOf(user.id);
  const id = profile.stripe_subscription_id;
  if (!id) return json({ canceled: false, reason: "no subscription" });
  const r = await stripe("DELETE", `/subscriptions/${encodeURIComponent(id)}`);
  // Already canceled (or gone) counts as done.
  let done = r.ok || r.status === 404 || r.data?.error?.code === "resource_missing";
  if (!done) {
    const check = await stripe("GET", `/subscriptions/${encodeURIComponent(id)}`);
    done = check.ok && ["canceled", "incomplete_expired"].includes(check.data.status);
  }
  if (!done) {
    console.error("cancel failed", r.status, JSON.stringify(r.data).slice(0, 500));
    return json({ error: "Couldn't cancel the subscription. Try again, or cancel it from Manage subscription." }, 502);
  }
  // Plus ends now; the webhook will confirm. Recorded here too, so a deleted account never keeps a paid status.
  const update: Record<string, unknown> = { stripe_status: "canceled", updated_at: new Date().toISOString() };
  if (profile.plus_source !== "paddle") Object.assign(update, { plan: "free", plus_until: new Date().toISOString() });
  await admin.from("profiles").update(update).eq("user_id", user.id);
  return json({ canceled: true });
}

Deno.serve(async (req) => {
  const path = new URL(req.url).pathname;
  if (req.method !== "POST") return json({ error: "not found" }, 404);
  const user = await signedInUser(req);
  if (!user) return json({ error: "Sign in again." }, 401);
  if (path.endsWith("/checkout")) return checkout(req, user);
  if (path.endsWith("/portal")) return portal(user);
  if (path.endsWith("/cancel")) return cancel(user);
  return json({ error: "not found" }, 404);
});
