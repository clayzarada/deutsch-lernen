// Small helpers shared by the billing and stripe functions: the Stripe REST API with plain fetch.
//
// Stripe's API takes form-encoded bodies with bracketed keys (line_items[0][price]=...). We pin the API version,
// so the objects we read (subscriptions, invoices) always have the same shape, whatever the account's default is.
// Managed Payments (Stripe as merchant of record) became generally available in 2026-04-22.dahlia.
export const STRIPE_VERSION = "2026-04-22.dahlia";

// Read on every request (trimmed), so a secret added or changed later is picked up without a redeploy.
export const env = (name: string) => (Deno.env.get(name) ?? "").trim();

// {a: {b: 1}, c: [x]} -> "a[b]=1&c[0]=x"
export function form(data: Record<string, unknown>, prefix = "", out = new URLSearchParams()) {
  for (const [k, v] of Object.entries(data)) {
    if (v === undefined || v === null) continue;
    const key = prefix ? `${prefix}[${k}]` : k;
    if (typeof v === "object") form(v as Record<string, unknown>, key, out);
    else out.append(key, String(v));
  }
  return out;
}

export async function stripe(method: string, path: string, body?: Record<string, unknown>) {
  const r = await fetch(`https://api.stripe.com/v1${path}`, {
    method,
    headers: {
      "authorization": `Bearer ${env("STRIPE_SECRET_KEY")}`,
      "stripe-version": STRIPE_VERSION,
      ...(body ? { "content-type": "application/x-www-form-urlencoded" } : {}),
    },
    body: body ? form(body).toString() : undefined,
  });
  const j = await r.json().catch(() => ({}));
  return { ok: r.ok, status: r.status, data: j as Record<string, any> };
}

export const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// Statuses that mean "the customer is paying (or about to)". past_due keeps Plus while Stripe retries the card.
export const PAYING = ["active", "trialing", "past_due"];

export const TOLERANCE = 300; // seconds: older webhook signatures are rejected (replay protection)

async function hmacHex(secret: string, text: string) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(text));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Compares in constant time, so the answer's timing says nothing about how much of a signature was right.
function sameText(a: string, b: string) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

// Stripe-Signature: t=1492774577,v1=<hex>[,v1=<hex>...]. Signed text is "<t>.<raw body>".
export async function verified(header: string, raw: string, secret: string, now = Date.now() / 1000) {
  let t = "";
  const sigs: string[] = [];
  for (const part of header.split(",")) {
    const [k, v] = part.trim().split("=", 2);
    if (k === "t") t = v;
    else if (k === "v1" && v) sigs.push(v);  // more than one while a secret is being rolled
  }
  if (!secret || !/^\d+$/.test(t) || !sigs.length) return false;
  if (Math.abs(now - Number(t)) > TOLERANCE) return false;
  const expected = await hmacHex(secret, `${t}.${raw}`);
  return sigs.some((s) => sameText(expected, s));
}

export const idOf = (v: unknown) => typeof v === "string" ? v : (v as { id?: string } | null)?.id;

// The subscription an event is about (invoices keep it under parent.subscription_details since API 2025-03-31).
export function subscriptionIdOf(event: Record<string, any>) {
  const o = event.data?.object ?? {};
  const type = String(event.type);
  if (type === "checkout.session.completed") return o.mode === "subscription" ? idOf(o.subscription) : undefined;
  if (type.startsWith("customer.subscription.")) return o.id as string | undefined;
  if (type === "invoice.paid" || type === "invoice.payment_failed") {
    return idOf(o.parent?.subscription_details?.subscription ?? o.subscription);
  }
}

// The account set at checkout. Only our billing function creates sessions, so this is our own value.
export function userHintOf(event: Record<string, any>) {
  if (event.type !== "checkout.session.completed") return undefined;
  const o = event.data?.object ?? {};
  const id = o.metadata?.user_id ?? o.client_reference_id;
  return typeof id === "string" && UUID.test(id) ? id : undefined;
}

// In test mode anyone could "buy" Plus with Stripe's public test card. Only accounts listed in STRIPE_TEST_TESTERS
// get Plus from test-mode payments; live payments count for everyone.
export function testerAllowed(userId: string, livemode: boolean, testers = env("STRIPE_TEST_TESTERS")) {
  if (livemode) return true;
  return testers.split(",").map((s) => s.trim()).filter(Boolean).includes(userId);
}

// End of the paid period. Since API version 2025-03-31 it lives on the subscription items, not the subscription.
export function periodEnd(sub: Record<string, any>) {
  const ends = (sub.items?.data ?? []).map((i: any) => Number(i.current_period_end)).filter(Boolean);
  const end = ends.length ? Math.max(...ends) : Number(sub.current_period_end) || 0;
  return end ? new Date(end * 1000) : null;
}
