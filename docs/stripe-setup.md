# Selling Plus with Stripe (Managed Payments)

This guide moves Plus payments from Paddle to **Stripe Managed Payments**, where Stripe is the merchant of record:
it charges the buyer, works out and pays sales tax and VAT, sends receipts and invoices, and handles disputes.
The app and the server code are ready. These are the steps only you can do, in order.

Nothing changes for buyers until step 9 (editing `plus.json`). Until then the app keeps using Paddle.

What the code does, in short:

- `supabase/functions/billing`: the app calls it with the signed-in user's token. It makes a Stripe Checkout page
  for that account (`/checkout`), opens Stripe's "manage subscription" page (`/portal`), and cancels the subscription
  when someone deletes their account (`/cancel`).
- `supabase/functions/stripe`: Stripe's webhook. It checks Stripe's signature, fetches the subscription from Stripe
  and turns Plus on or off in `profiles`, the same way the Paddle webhook does (3 grace days past the paid period).
- `supabase/migrations/0005_stripe.sql`: adds the Stripe columns to `profiles`.

## 1. Create the Stripe account and turn on Managed Payments

1. Sign up at stripe.com with the business details of Zarada Holdings Group LLC (a US business is supported).
   Finish the account activation (business details, bank account for payouts, identity check).
2. Under **Settings → Business → Public details**, set the **support email** to support@deutschlernenapp.com.
   Stripe's buyer support (through Link, see below) sends escalated cases to this address and expects an answer
   within 48 hours, or it may refund the buyer on its own.
3. Under **Settings → Business → Public details**, set the **statement descriptor** to something buyers recognize,
   for example `DEUTSCHLERNEN`. Card statements will show `LINK.COM* DEUTSCHLERNEN`.
4. Open **Settings → Managed Payments** (dashboard.stripe.com/settings/managed-payments), read and accept the
   Managed Payments terms, and turn it on.
5. Do steps 2 to 7 twice: first in a **sandbox** (test mode, top left account menu → Sandboxes), later again in
   the live account. Test and live have separate products, prices, keys and webhooks.

## 2. Create the product and the two prices

1. **Product catalog → Create product**.
2. Name: `Deutsch lernen Plus`. Description: `AI practice, marking, AI flashcards, study coach and cloud backup for
   the Deutsch lernen app.`
3. **Product tax code**: choose **`txcd_10105003` "Artificial Intelligence as a Service (AIaaS) - Cloud Based &
   Downloaded - Personal Use"**. It fits Plus exactly: a downloaded desktop app working together with cloud AI,
   bought by people for personal use. It is on Stripe's list of codes eligible for Managed Payments (added June 2026).
   In the picker it is marked "Eligible for Managed Payments". If it isn't offered, use `txcd_10103100` "SaaS -
   electronic download - personal use" instead.
4. First price: **$9.99 USD, Recurring, Monthly**. Under **Include tax in price** leave **No** (tax is added on top at
   checkout, as the website already says).
5. Save, then on the product page add a second price with **+**: **$79.00 USD, Recurring, Yearly**, tax not included.
6. Copy each price's id (`price_...`). You need them in step 5.

## 3. Customer portal (Manage subscription)

**Settings → Billing → Customer portal**:

1. Turn on: **Customers can update payment methods**, **view invoice history**, **update billing address**.
2. **Cancel subscriptions**: on, **Cancel at end of billing period** (Plus stays until the paid time ends).
   Add the cancellation reason survey only if you want it. No retention offers: they're a dark pattern we avoid.
3. **Switch plans**: on, and add both prices (monthly and yearly) of the Plus product.
4. Business information: link the terms (https://deutschlernenapp.com/terms/) and privacy policy
   (https://deutschlernenapp.com/privacy/).
5. Save. Buyers can also manage their subscription at link.com, since Stripe sells through Link.

**Settings → Checkout** (optional): add the links to the terms and privacy policy, so the Stripe checkout page
shows them.

## 4. Webhook endpoint

**Developers → Webhooks → Add endpoint**:

1. Endpoint URL: `https://zarusstgbgyvongoterq.supabase.co/functions/v1/stripe`
2. API version: **2026-04-22.dahlia** (or newer; the code reads both the old and new invoice shapes, and fetches
   the subscription itself with that version).
3. Events to send:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
4. Save, then **Reveal** the **Signing secret** (`whsec_...`). You need it in step 5.

## 5. Supabase secrets

Supabase dashboard → **Edge Functions → Secrets**. Add (names only here; paste the values yourself):

| Name | What |
| --- | --- |
| `STRIPE_SECRET_KEY` | Stripe → Developers → API keys → Secret key (`sk_test_...` in the sandbox, `sk_live_...` later) |
| `STRIPE_WEBHOOK_SECRET` | the endpoint's signing secret from step 4 (`whsec_...`) |
| `STRIPE_PRICE_MONTHLY` | the monthly price id (`price_...`) |
| `STRIPE_PRICE_YEARLY` | the yearly price id |
| `STRIPE_SUCCESS_URL` | page shown after paying, e.g. `https://deutschlernenapp.com/checkout/done/` (see step 10) |
| `STRIPE_CANCEL_URL` | page shown when the buyer goes back, e.g. `https://deutschlernenapp.com/#pricing` |
| `STRIPE_TEST_TESTERS` | comma-separated account ids that may get Plus from **test** payments (step 7) |
| `STRIPE_PORTAL_RETURN_URL` | optional: where "Return" in the portal goes (defaults to the success page) |

Test or live is decided by which keys you paste: sandbox keys mean test mode. Test-mode purchases only give Plus to
the accounts in `STRIPE_TEST_TESTERS`, so nobody can get Plus with Stripe's public test card. Live payments count
for everyone.

If you prefer a restricted key (`rk_...`) instead of the full secret key, give it write access to **Checkout
Sessions**, **Customer portal** and **Subscriptions**.

## 6. Database and functions

1. Supabase → **SQL editor**: run `supabase/migrations/0005_stripe.sql` (safe to run again). Do this **before**
   deploying the functions: the new code writes the new columns.
2. Deploy the functions (Supabase CLI, from the app folder, signed in to the project):
   ```
   supabase functions deploy billing
   supabase functions deploy stripe --no-verify-jwt
   supabase functions deploy paddle --no-verify-jwt
   ```
   - `billing` keeps **Verify JWT on**: only signed-in users call it.
   - `stripe` must have **Verify JWT off**: Stripe can't sign in; the function checks Stripe's signature instead.
     Check it in the dashboard under Edge Functions → stripe → Details.
   - `paddle` is redeployed because it now leaves alone a Plus that Stripe granted (it stays JWT-off as before).

## 7. Test in the sandbox

1. Find your own account id: Supabase → **Authentication → Users**, the id of your email. Put it in
   `STRIPE_TEST_TESTERS`.
2. Upload a test switch file to the website, e.g. `plus-test.json`:
   ```json
   { "sales_open": true, "provider": "stripe" }
   ```
   and start the app with `DL_PLUS_INFO_URL=https://deutschlernenapp.com/plus-test.json`, so only your copy of the
   app sees the Upgrade buttons and uses Stripe.
3. In the app: Settings → Account & Plus → sign in → **Upgrade**. The Stripe checkout opens in the browser.
4. Pay with the test card `4242 4242 4242 4242`, any future date, any CVC. Try a few billing addresses (a US state,
   Germany, Turkey) to see the tax change.
5. Back in the app, Plus should show up within a minute (the app checks every 10 seconds).
6. Check in Stripe: **Developers → Webhooks → your endpoint**: all deliveries answered 200. In Supabase: Edge
   Functions → stripe → Logs: no errors.
7. Try **Manage subscription** (Stripe's portal opens), switch to yearly, cancel at period end.
8. Cancel immediately in the Stripe dashboard (Subscription → Cancel → Immediately): Plus goes away in the app
   after Refresh.
9. Optional, a failed renewal: in the portal replace the card with `4000 0000 0000 0341` (it saves, but charges
   fail), then let a renewal happen (Stripe's test clocks under Billing → Test clocks move time forward). Plus should
   stay during Stripe's retries and end when Stripe gives up and cancels the subscription.
10. Delete account with an active test subscription: the subscription shows as canceled in Stripe.
11. Buy with a second account that is **not** in `STRIPE_TEST_TESTERS`: the payment goes through in Stripe, but no
   Plus (the function log says "isn't a tester").

## 8. Go live

1. Repeat steps 1 to 4 in the live account (product, prices, portal, webhook).
2. Replace the secrets with the live ones: `STRIPE_SECRET_KEY` (`sk_live_...`), `STRIPE_WEBHOOK_SECRET` (live
   endpoint), `STRIPE_PRICE_MONTHLY`, `STRIPE_PRICE_YEARLY`. No redeploy is needed: the functions read secrets on
   every request.
3. Your tester account still holds the sandbox subscription in `profiles`. Before buying for real with it, clear
   it in Supabase → Table editor → profiles (set `stripe_customer_id`, `stripe_subscription_id` and `stripe_status`
   to empty), or cancel the test subscription first; otherwise checkout says you already have Plus.
4. Optionally do one real purchase yourself and refund it.

## 9. Switch the app: `plus.json`

On the website, change `plus.json` to:

```json
{
  "sales_open": true,
  "provider": "stripe",
  "note": "provider: stripe or paddle. The app checks this file to show the Upgrade buttons and pick the payment provider."
}
```

The app picks it up within 10 minutes, without an update. Setting `"provider": "paddle"` (or leaving it out) goes
back to Paddle. Existing Paddle subscribers keep working either way: Manage subscription and Delete account find
their Paddle subscription.

## 10. Website and legal pages (to change in the website repo)

The app no longer needs the website's checkout page; Stripe hosts the checkout. What to change:

- **New success page** (`/checkout/done/` and `/tr/checkout/done/`): "Thank you, Plus is yours. Go back to the app;
  it shows Plus within a minute (or press Refresh under Settings → Account & Plus)." This is `STRIPE_SUCCESS_URL`.
- **`/checkout/` and `/tr/checkout/`**: remove the Paddle script, tokens and overlay. Either delete the page (and
  redirect it to `/#pricing`) or keep it only for old app versions that still open it while Paddle is off. Old
  app versions (before this change) always open this page, so keep a short note there: "Update the app to buy Plus"
  or leave Paddle running on it until most people have updated.
- **Fine print** (was "Payments are handled by Paddle, our reseller and merchant of record"): "Payments are handled
  by Stripe, the merchant of record for Plus. At checkout and on receipts, Stripe appears as Link (Stripe's checkout
  service), and card statements show LINK.COM* DEUTSCHLERNEN. Tax is added at checkout where it applies."
- **Home page pricing** (`/` and `/tr/`): "Prices are in US dollars" becomes "Prices are in US dollars; checkout may
  show them in your local currency" (Stripe's Adaptive Pricing is always on with Managed Payments).
  "Tax is added at checkout" stays true.
- **Terms** (`/terms/`, `/tr/terms/`), the "Seller" clause: replace "Orders are processed by our online reseller
  Paddle.com, which is the merchant of record for all orders. Paddle handles payment, tax and invoices, and its
  buyer terms also apply" with Stripe (through Link) as merchant of record that handles payment, tax, invoices and
  transaction support, and that Link's buyer terms apply to the purchase. Check the exact legal name of the seller
  and the buyer terms to link in Stripe's Managed Payments terms before publishing.
- **Privacy** (`/privacy/`, `/tr/privacy/`): "Payment is handled by Paddle" → Stripe. In the list of processors,
  replace Paddle.com with **Stripe (including Link)**: sells Plus as merchant of record (checkout, payment, tax,
  invoices, refunds, disputes) and collects payment and billing details under its own privacy policy.
- **Refunds** (`/refunds/`, `/tr/refunds/`): "use the link in your Paddle receipt to contact Paddle, our reseller"
  → "use the link in your receipt from Link, or support.link.com". "Refunds go back ... through Paddle" → "through
  Stripe". Our 14-day full refund promise stays; note that Stripe may also refund a buyer itself (up to 60 days)
  when its support handles a case.
- **Footer / about text** mentioning Paddle anywhere else: replace with Stripe.

## Running it

- **Refunds**: refund in the Stripe dashboard (Payments → the payment → Refund). A refund alone does not end Plus.
  To end Plus at the same time, also cancel the subscription **immediately** (Subscriptions → Cancel → Immediately);
  the webhook then turns Plus off. (The Paddle webhook did both automatically.)
- **Disputes** are handled by Stripe for you.
- **Receipts and renewal emails** come from Link; your Stripe email settings don't change them. Under
  Settings → Billing → Subscriptions and emails you can still turn on upcoming-renewal reminders.
- **Where to look when something's wrong**: Stripe → Developers → Webhooks (failed deliveries are retried for 3
  days) and Supabase → Edge Functions → stripe / billing → Logs.
