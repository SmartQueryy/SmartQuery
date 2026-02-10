"""
Stripe Checkout API for SmartQuery subscription payments.

Requires in .env:
- STRIPE_SECRET_KEY (or Secret_key) - from Stripe Dashboard
- STRIPE_PRO_MONTHLY_PRICE_ID - create Price in Stripe for $19/month
- STRIPE_PRO_ANNUAL_PRICE_ID - create Price in Stripe for $182.40/year
"""

import os
from typing import Optional

import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Support both standard and legacy env var names
stripe.api_key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("Secret_key")
STRIPE_PRO_MONTHLY_PRICE_ID = os.getenv("STRIPE_PRO_MONTHLY_PRICE_ID")
STRIPE_PRO_ANNUAL_PRICE_ID = os.getenv("STRIPE_PRO_ANNUAL_PRICE_ID")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

router = APIRouter(prefix="/stripe", tags=["stripe"])


class CreateCheckoutSessionRequest(BaseModel):
    """Request to create a Stripe Checkout session for Pro subscription."""

    annual: bool = False
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    customer_email: Optional[str] = None


@router.post("/create-checkout-session")
async def create_checkout_session(body: CreateCheckoutSessionRequest):
    """
    Create a Stripe Checkout Session for Pro subscription (monthly or annual).
    Returns the session URL to redirect the user to Stripe-hosted checkout.
    """
    if not stripe.api_key:
        raise HTTPException(
            status_code=500,
            detail="Stripe is not configured. Set STRIPE_SECRET_KEY in .env",
        )

    price_id = STRIPE_PRO_ANNUAL_PRICE_ID if body.annual else STRIPE_PRO_MONTHLY_PRICE_ID
    if not price_id:
        raise HTTPException(
            status_code=500,
            detail="Stripe price not configured. Set STRIPE_PRO_MONTHLY_PRICE_ID and STRIPE_PRO_ANNUAL_PRICE_ID in .env",
        )

    success_url = body.success_url or f"{FRONTEND_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = body.cancel_url or f"{FRONTEND_URL}/checkout/cancel"

    try:
        session_params = {
            "mode": "subscription",
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "allow_promotion_codes": True,
        }

        if body.customer_email:
            session_params["customer_email"] = body.customer_email

        session = stripe.checkout.Session.create(**session_params)

        return {
            "success": True,
            "url": session.url,
            "session_id": session.id,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
