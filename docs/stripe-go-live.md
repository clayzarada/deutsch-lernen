# Going live with Stripe: approval-day checklist

Everything that could be done before the live Stripe account is approved is done:

- The sandbox was tested end to end on 2026-11-21: buying, switching to yearly in euros, cancelling at the end of the
  period, cancelling now. 7 webhook deliveries, none failed.
- The Supabase database update and the `billing`, `stripe` and `paddle` functions are live.
- The website's launch changes wait on the `stripe-live` branch of `deutschlernenapp-site`.

Live mode in the Stripe dashboard stays locked until activation (every live page redirects to test mode), so the
steps below happen on approval day. They take about 30 minutes.

## 0. Before approval: activation (owner)

Stripe → **Activate payments** for the account "Zarada Holdings Group LLC" (acct_1UeECbEhU4c63nIw). It typically asks for:

- **Business type:** Registered business → LLC. Legal name, **EIN**, registered address, phone.
- **Business details:**
  - Website: https://deutschlernenapp.com
  - Industry: software / digital products
  - A short description, for example "Desktop app for learning German; optional Plus subscription with AI features."
- **Representative:** name, date of birth, home address, email, phone, title, and SSN or an ID document.
- **Owners** with 25% or more.
- **Bank account** in the LLC's name for payouts.
- **Two-step sign-in** for the Stripe login.

Stripe reviews the website. It already has terms, privacy and refund pages, prices and a contact address.

## 1. Live Stripe setup (the dashboard in live mode; same as the sandbox)

1. **Settings → Managed Payments → Get started.**
   - Category: `txcd_10105003` "Artificial Intelligence as a Service (AIaaS) - Cloud Based & Downloaded - Personal Use".
   - Accept the Managed Payments terms. That step is the owner's.
2. **Product** "Deutsch lernen Plus", same tax code. Description: "AI practice, marking, AI flashcards, study coach
   and cloud backup for the Deutsch lernen app."
   - **Monthly** price: $9.99 USD, recurring monthly, tax **not** included. Then **Edit → Add a price by currency → EUR
     9.99, Include tax in price: Yes**.
   - **Yearly** price: $79.00 USD, recurring yearly, tax not included, plus **EUR 79.00, Include tax: Yes**.
   - Note both `price_...` ids.
3. **Settings → Billing → Customer portal:**
   - Switch plans: on, with both prices.
   - Cancel: at the end of the billing period.
   - Phone number: off.
   - Payment methods and invoices: on.
   - No retention coupons or offers.
   - Save.
4. **Settings → Business → Public details:** support email support@deutschlernenapp.com, statement descriptor
   `DEUTSCHLERNEN`. Also the terms and privacy links (they unlock after activation).
5. **Workbench → Webhooks → Add destination:**
   - Scope: Your account. Payload style: Snapshot. API version: the latest **dahlia** release.
   - Events: `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`,
     `customer.subscription.deleted`, `invoice.paid`, `invoice.payment_failed`.
   - Name: "Deutsch lernen Plus (Supabase)". URL: `https://zarusstgbgyvongoterq.supabase.co/functions/v1/stripe`.

## 2. Supabase secrets (Edge Functions → Secrets)

Replace the sandbox values. The functions read secrets on every request, so nothing needs to be redeployed.

| Secret | New value | Who |
| --- | --- | --- |
| `STRIPE_SECRET_KEY` | live secret key `sk_live_...` (Developers → API keys; copy it straight in, it may only show once) | owner |
| `STRIPE_WEBHOOK_SECRET` | the live destination's signing secret `whsec_...` | owner |
| `STRIPE_PRICE_MONTHLY` | live monthly `price_...` | Claude |
| `STRIPE_PRICE_YEARLY` | live yearly `price_...` | Claude |

These stay as they are:

- `STRIPE_SUCCESS_URL`: https://deutschlernenapp.com/checkout/done/
- `STRIPE_CANCEL_URL`: https://deutschlernenapp.com/#pricing
- `STRIPE_TEST_TESTERS`: only matters in test mode.

The owner's account still holds the sandbox subscription ids. Clear them first, or checkout says "You already
have Plus":

```sql
update public.profiles set stripe_customer_id = null, stripe_subscription_id = null, stripe_status = null
where user_id = '9d6ff94a-1e24-4680-8356-ef7e16b61309';
```

## 3. Website (repo `deutschlernenapp-site`)

1. On the `stripe-live` branch, set the **effective date** on the terms, privacy and refund pages (English and
   Turkish) to the launch date.
2. Merge `stripe-live` into `main` and push. Netlify publishes it.

The branch does these things:

- `plus.json` → `{"sales_open": true, "provider": "stripe"}`: the app shows Upgrade and uses Stripe within 10 minutes.
- The pricing buttons become "Get Plus in the app", and the "notify me" form goes.
- The fine print, terms, privacy and refund pages name Stripe as merchant of record, shown to buyers as Link
  ("Sold through Link"; statements show `LINK.COM* DEUTSCHLERNEN`).
- `/checkout/` tells people on app versions before 3.0 to update. Those versions open the website to buy, and
  Paddle isn't used any more.
- Email the people who signed up for the launch note (Netlify → Forms → plus-launch), once, then delete the list,
  as the privacy page promises.

**Release 3.0 before or together with this step**, so people can update when asked.

## 4. Check

- One real purchase with your own card (monthly), then refund it in Stripe and cancel the subscription immediately.
- Confirm Plus turns on and off. Stripe → Webhooks shows deliveries with no failures; Supabase → Edge Functions →
  `stripe` → Logs shows no errors.
- After that, Paddle can be retired: leave its function deployed (it ignores Stripe customers), and close the Paddle
  account once nobody holds a Paddle subscription.
