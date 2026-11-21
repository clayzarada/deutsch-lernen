// Checks for the Stripe helpers. Run with: deno test supabase/functions/_shared/stripe_test.ts
import { form, periodEnd, subscriptionIdOf, testerAllowed, userHintOf, verified } from "./stripe.ts";

function assert(ok: unknown, msg = "assertion failed") {
  if (!ok) throw new Error(msg);
}

async function sign(secret: string, t: number, raw: string) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${t}.${raw}`));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

Deno.test("signature: good, wrong, old, rolled secret", async () => {
  const raw = '{"id":"evt_1","type":"invoice.paid"}', now = 1_800_000_000;
  const good = await sign("whsec_a", now, raw);
  assert(await verified(`t=${now},v1=${good}`, raw, "whsec_a", now), "good signature");
  assert(await verified(`t=${now},v1=deadbeef,v1=${good}`, raw, "whsec_a", now), "second v1 while rolling");
  assert(!(await verified(`t=${now},v1=${good}`, raw + " ", "whsec_a", now)), "changed body");
  assert(!(await verified(`t=${now},v1=${good}`, raw, "whsec_b", now)), "other secret");
  assert(!(await verified(`t=${now},v1=${good}`, raw, "whsec_a", now + 301)), "too old");
  assert(!(await verified(`t=${now},v0=${good}`, raw, "whsec_a", now)), "only v1 counts");
  assert(!(await verified("", raw, "whsec_a", now)), "no header");
  assert(!(await verified(`t=${now},v1=${good}`, raw, "", now)), "no secret set");
});

Deno.test("events point at their subscription and account", () => {
  const uid = "0b6c2f4e-1111-4222-8333-944455556666";
  const done = { type: "checkout.session.completed", data: { object: { mode: "subscription", subscription: "sub_1", client_reference_id: uid, metadata: { user_id: uid } } } };
  assert(subscriptionIdOf(done) === "sub_1" && userHintOf(done) === uid);
  const forged = { type: "checkout.session.completed", data: { object: { mode: "subscription", subscription: "sub_1", client_reference_id: "x' or 1=1" } } };
  assert(userHintOf(forged) === undefined, "not a uuid");
  assert(subscriptionIdOf({ type: "customer.subscription.deleted", data: { object: { id: "sub_2" } } }) === "sub_2");
  assert(subscriptionIdOf({ type: "invoice.paid", data: { object: { parent: { subscription_details: { subscription: "sub_3" } } } } }) === "sub_3");
  assert(subscriptionIdOf({ type: "invoice.payment_failed", data: { object: { subscription: { id: "sub_4" } } } }) === "sub_4");
  assert(subscriptionIdOf({ type: "charge.succeeded", data: { object: { id: "ch_1" } } }) === undefined);
});

Deno.test("test-mode purchases only count for listed testers", () => {
  assert(testerAllowed("a", true, ""));
  assert(!testerAllowed("a", false, ""));
  assert(testerAllowed("a", false, " b , a "));
});

Deno.test("period end comes from the items", () => {
  assert(periodEnd({ items: { data: [{ current_period_end: 1_800_000_000 }] } })!.getTime() === 1_800_000_000_000);
  assert(periodEnd({ current_period_end: 1_700_000_000 })!.getTime() === 1_700_000_000_000);
  assert(periodEnd({}) === null);
});

Deno.test("form encoding uses Stripe's bracket keys", () => {
  const f = form({ line_items: [{ price: "price_1", quantity: 1 }], managed_payments: { enabled: true }, skip: undefined });
  assert(f.toString() === "line_items%5B0%5D%5Bprice%5D=price_1&line_items%5B0%5D%5Bquantity%5D=1&managed_payments%5Benabled%5D=true");
});
