"""
Stripe router — checkout session, webhook handler, customer portal.
"""

import logging
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db
from dependencies import get_current_user
from models.subscription import Subscription
from models.user import User

router = APIRouter(prefix="/stripe", tags=["stripe"])
logger = logging.getLogger(__name__)
settings = get_settings()

# Map Stripe price IDs → plan names
PRICE_TO_PLAN: dict[str, str] = {}


def _init_price_map():
    """Build price → plan mapping after settings are loaded."""
    global PRICE_TO_PLAN
    PRICE_TO_PLAN = {
        settings.stripe_price_starter_monthly: "starter",
        settings.stripe_price_starter_yearly: "starter",
        settings.stripe_price_pro_monthly: "pro",
        settings.stripe_price_pro_yearly: "pro",
        settings.stripe_price_studio_monthly: "studio",
        settings.stripe_price_studio_yearly: "studio",
    }
    # Remove empty keys
    PRICE_TO_PLAN = {k: v for k, v in PRICE_TO_PLAN.items() if k}


# ── Schemas ────────────────────────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    price_id: str
    success_url: str = "https://hsbvectoai.com/success"
    cancel_url: str = "https://hsbvectoai.com/pricing"


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/create-checkout")
async def create_checkout(
    req: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a Stripe Checkout Session and return the URL."""
    stripe.api_key = settings.stripe_secret_key
    _init_price_map()

    if req.price_id not in PRICE_TO_PLAN:
        raise HTTPException(status_code=400, detail="Geçersiz fiyat planı.")

    # Get or create Stripe customer
    customer_id = user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(email=user.email, metadata={"user_id": user.id})
        customer_id = customer.id
        user.stripe_customer_id = customer_id

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": req.price_id, "quantity": 1}],
        success_url=req.success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=req.cancel_url,
        metadata={"user_id": str(user.id)},
    )

    return {"url": session.url}


@router.get("/portal")
async def customer_portal(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate Stripe Customer Portal URL for subscription management."""
    stripe.api_key = settings.stripe_secret_key

    if not user.stripe_customer_id:
        raise HTTPException(status_code=404, detail="Stripe müşteri kaydı bulunamadı.")

    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url="https://hsbvectoai.com/dashboard",
    )
    return {"url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events — subscription lifecycle."""
    stripe.api_key = settings.stripe_secret_key
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Webhook imzası geçersiz.")

    _init_price_map()

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        await _handle_subscription_upsert(data, db)

    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(data, db)

    elif event_type == "invoice.payment_failed":
        logger.warning("Payment failed for customer %s", data.get("customer"))

    return {"received": True}


# ── Internal helpers ───────────────────────────────────────────────────────────

async def _get_user_by_stripe_customer(customer_id: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    return result.scalar_one_or_none()


async def _handle_subscription_upsert(sub: dict, db: AsyncSession):
    customer_id = sub["customer"]
    user = await _get_user_by_stripe_customer(customer_id, db)
    if not user:
        logger.warning("No user found for Stripe customer %s", customer_id)
        return

    price_id = sub["items"]["data"][0]["price"]["id"]
    plan = PRICE_TO_PLAN.get(price_id, "free")
    interval = sub["items"]["data"][0]["plan"]["interval"]
    status = sub["status"]
    period_end = datetime.fromtimestamp(sub["current_period_end"], tz=timezone.utc)

    # Update user plan
    user.plan = plan if status in ("active", "trialing") else "free"

    # Upsert subscription record
    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    existing = result.scalar_one_or_none()

    if existing:
        existing.stripe_subscription_id = sub["id"]
        existing.plan = plan
        existing.interval = interval
        existing.status = status
        existing.current_period_end = period_end
        existing.cancel_at_period_end = sub.get("cancel_at_period_end", False)
        existing.updated_at = datetime.now(timezone.utc)
    else:
        db.add(Subscription(
            user_id=user.id,
            stripe_subscription_id=sub["id"],
            stripe_customer_id=customer_id,
            plan=plan,
            interval=interval,
            status=status,
            current_period_end=period_end,
            cancel_at_period_end=sub.get("cancel_at_period_end", False),
            updated_at=datetime.now(timezone.utc),
        ))

    logger.info("Subscription upserted: user=%s plan=%s status=%s", user.id, plan, status)


async def _handle_subscription_deleted(sub: dict, db: AsyncSession):
    customer_id = sub["customer"]
    user = await _get_user_by_stripe_customer(customer_id, db)
    if not user:
        return

    user.plan = "free"

    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == sub["id"])
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.status = "canceled"
        existing.updated_at = datetime.now(timezone.utc)

    logger.info("Subscription canceled: user=%s", user.id)
