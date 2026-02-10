# Stripe Setup for SmartQuery Pro

## 1. Create Products & Prices in Stripe

1. Go to [Stripe Dashboard → Products](https://dashboard.stripe.com/products)
2. Click **Add product**
3. Create **SmartQuery Pro Monthly**:
   - Name: `SmartQuery Pro`
   - Description: `Pro plan - 15 projects, 500 AI queries/month`
   - Pricing: **Recurring**, `$19.00` USD, **Monthly**
   - Save → copy the **Price ID** (starts with `price_`)

4. Create **SmartQuery Pro Annual**:
   - Add another price to the same product, or create a new product
   - Pricing: **Recurring**, `$182.40` USD, **Yearly** (or `$15.20`/month)
   - Save → copy the **Price ID**

## 2. Add Price IDs to .env

In your project root `.env`, set:

```
STRIPE_PRO_MONTHLY_PRICE_ID=price_xxxxxxxxxxxxx
STRIPE_PRO_ANNUAL_PRICE_ID=price_xxxxxxxxxxxxx
```

## 3. Verify Keys

You should already have:
- `STRIPE_SECRET_KEY` or `Secret_key` – from [Stripe API Keys](https://dashboard.stripe.com/apikeys)
- Use **test mode** keys for development (`sk_test_...`, `pk_test_...`)

## 4. Flow

1. User clicks **Start Pro Trial** on pricing page
2. Backend creates a Stripe Checkout Session
3. User is redirected to Stripe-hosted checkout
4. After payment → `/checkout/success`
5. If cancelled → `/checkout/cancel`

## 5. Testing

Use Stripe test cards:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- 3D Secure: `4000 0025 0000 3155`

See [Stripe Testing](https://docs.stripe.com/testing) for more.
