// Deutsch lernen Plus: the Paddle side.
//
//   POST .../paddle/webhook   Paddle's notifications (signed). Turns Plus on or off for the account.
//   POST .../paddle/portal    Signed-in user: returns a link to Paddle's "manage subscription" page.
//
// Secrets (Supabase dashboard -> Edge Functions -> Secrets):
//   PADDLE_WEBHOOK_SECRET   from Paddle -> Developer tools -> Notifications (the destination's secret key)
//   PADDLE_API_KEY          from Paddle -> Developer tools -> Authentication (server-side API key)
//   PADDLE_ENV              "sandbox" while testing, "live" for real payments
// Turn OFF "Verify JWT" for this function: Paddle can't sign in, so the webhook checks Paddle's signature
// instead, and the portal checks the user's sign-in itself.
import { createClient } from "npm:@supabase/supabase-js@2";

const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
  auth: { persistSession: false },
});
// Read on every request (trimmed), so a secret added or changed later is picked up without a redeploy.
const env = (name: string) => (Deno.env.get(name) ?? "").trim();
const apiBase = () => env("PADDLE_ENV") === "live" ? "https://api.paddle.com" : "https://sandbox-api.paddle.com";
const GRACE_DAYS = 3; // Plus stays on this long past the period end, so a slightly late renewal never cuts anyone off

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

async function hmacHex(secret: string, text: string) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(text));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Paddle-Signature: ts=1671552777;h1=<hex>. Signed text is "<ts>:<raw body>". Reject anything older than 5 minutes.
async function verified(req: Request, raw: string) {
  const header = req.headers.get("paddle-signature") ?? "";
  const secret = env("PADDLE_WEBHOOK_SECRET");
  let ts = "";
  const sigs: string[] = [];
  for (const part of header.split(";")) {
    const [k, v] = part.trim().split("=", 2);
    if (k === "ts") ts = v;
    else if (k === "h1" && v) sigs.push(v);  // more than one while a secret is being rotated
  }
  if (!secret) console.error("PADDLE_WEBHOOK_SECRET is not set");
  if (!secret || !ts || !sigs.length) return false;
  if (Math.abs(Date.now() / 1000 - Number(ts)) > 300) return false;
  const expected = await hmacHex(secret, `${ts}:${raw}`);
  return sigs.some((h1) => {
    if (h1.length !== expected.length) return false;
    let diff = 0;
    for (let i = 0; i < expected.length; i++) diff |= expected.charCodeAt(i) ^ h1.charCodeAt(i);
    return diff === 0;
  });
}

function addDays(iso: string, days: number) {
  return new Date(new Date(iso).getTime() + days * 86400000).toISOString();
}

async function findUserId(sub: Record<string, any>) {
  const fromCheckout = sub.custom_data?.user_id;
  if (fromCheckout) return fromCheckout as string;
  const { data } = await admin.from("profiles").select("user_id")
    .or(`paddle_subscription_id.eq.${sub.id},paddle_customer_id.eq.${sub.customer_id}`).limit(1).maybeSingle();
  return data?.user_id as string | undefined;
}

async function onSubscription(sub: Record<string, any>) {
  const userId = await findUserId(sub);
  if (!userId) {
    console.error("subscription without a known account", sub.id);
    return;
  }
  const status = sub.status as string; // active, trialing, past_due, paused, canceled
  const ends = sub.current_billing_period?.ends_at as string | undefined;
  const update: Record<string, unknown> = {
    paddle_customer_id: sub.customer_id, paddle_subscription_id: sub.id, updated_at: new Date().toISOString(),
  };
  if ((status === "active" || status === "trialing" || status === "past_due") && ends) {
    update.plan = "plus";
    update.plus_until = addDays(ends, GRACE_DAYS);
  } else if (status === "canceled" || status === "paused") {
    update.plan = "free";
    update.plus_until = new Date().toISOString();
  }
  const { error } = await admin.from("profiles").update(update).eq("user_id", userId);
  if (error) console.error("profile update failed", error);
}

async function portal(req: Request) {
  const token = (req.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "");
  const { data } = token ? await admin.auth.getUser(token) : { data: null };
  const user = data?.user;
  if (!user) return json({ error: "Sign in again." }, 401);
  const { data: profile } = await admin.from("profiles").select("paddle_customer_id, paddle_subscription_id").eq("user_id", user.id).maybeSingle();
  if (!profile?.paddle_customer_id) return json({ error: "There's no subscription on this account yet." }, 404);
  const r = await fetch(`${apiBase()}/customers/${profile.paddle_customer_id}/portal-sessions`, {
    method: "POST",
    headers: { "authorization": `Bearer ${env("PADDLE_API_KEY")}`, "content-type": "application/json" },
    body: JSON.stringify(profile.paddle_subscription_id ? { subscription_ids: [profile.paddle_subscription_id] } : {}),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) {
    console.error("portal session failed", r.status, JSON.stringify(j).slice(0, 300));
    return json({ error: "Couldn't open subscription settings. Try again later." }, 502);
  }
  return json({ url: j.data?.urls?.general?.overview });
}

Deno.serve(async (req) => {
  const path = new URL(req.url).pathname;
  if (req.method === "POST" && path.endsWith("/portal")) return portal(req);
  if (req.method === "POST" && path.endsWith("/webhook")) {
    const raw = await req.text();
    if (!(await verified(req, raw))) {
      console.error("webhook signature check failed");
      return json({ error: "bad signature" }, 401);
    }
    const event = JSON.parse(raw);
    if (String(event.event_type).startsWith("subscription.")) await onSubscription(event.data);
    return json({ ok: true });
  }
  return json({ error: "not found" }, 404);
});
