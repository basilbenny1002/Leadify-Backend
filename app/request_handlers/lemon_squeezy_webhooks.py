import datetime
from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
import os
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv
from dateutil import parser

from app.utils.billing_functions import add_credits_to_user, process_order_event

load_dotenv()

router = APIRouter()

# Supabase init
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
LEMON_SECRET = os.getenv("LEMON_WEBHOOK_SECRET")
LEMON_API_KEY = os.getenv("LEMON_SQUEEZY_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_signature(raw_body: bytes, signature: str) -> bool:
    """Verify LemonSqueezy webhook signature."""
    computed_signature = hmac.new(
        LEMON_SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_signature, signature)

@router.post("/webhooks/lemonsqueezy")
async def handle_lemon_webhook(
    request: Request,
    x_signature: str = Header(None)
):
    raw_body = await request.body()

    if not x_signature or not verify_signature(raw_body, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_name = payload.get("meta", {}).get("event_name")
    custom_data = payload.get("meta", {}).get("custom_data", {})
    user_id = custom_data.get("user_id")
    product_type = custom_data.get("product_type")

    print(payload)

    print(user_id)
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user ID")

    print(event_name)
    print(product_type)
    if product_type == "subscription":
        await process_subscription_event(event_name, payload, user_id)
    elif product_type == "topup":
        await process_order_event(payload, user_id)
    return {"status": "success"}

async def process_subscription_event(event_name: str, payload: dict, user_id: str):
    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    subscription_id = data.get("id")
    status = attributes.get("status")
    renews_at = parser.parse(attributes.get("renews_at")) if attributes.get("renews_at") else None
    ends_at = parser.parse(attributes.get("ends_at")) if attributes.get("ends_at") else None
    variant_id = attributes.get("variant_id")
    variant_name = attributes.get("variant_name", "Unknown Plan")
    product_id = attributes.get("product_id")
    product_name = attributes.get("product_name")
    billing_anchor = attributes.get("billing_anchor")
    created_at = parser.parse(attributes.get("created_at")) if attributes.get("created_at") else None
    card_brand = attributes.get("card_brand")
    card_last_four = attributes.get("card_last_four")

    # Check for existing subscription
    existing = supabase.from_("subscriptions").select("*").eq("user_id", user_id).maybe_single().execute()

    print(existing)

    sub_data = {
        "user_id": user_id,
        "subscription_id": subscription_id,
        "status": status,
        "renews_at": renews_at.isoformat() if renews_at else None,
        "ends_at": ends_at.isoformat() if ends_at else None,
        "plan_id": variant_id,
        "plan_name": variant_name,
        "product_id": product_id,
        "product_name": product_name,
        "billing_anchor": billing_anchor,
        "created_at": created_at.isoformat() if created_at else None,
        "card_brand": card_brand,
        "card_last_four": card_last_four
    }

    if event_name == "subscription_created":
        if existing and existing.data:
            supabase.from_("subscriptions").update(sub_data).eq("user_id", user_id).execute()
        else:
            supabase.from_("subscriptions").insert(sub_data).execute()
        print("Subscription created by", user_id)

        # Add credits on new subscription
        await add_credits_to_user(user_id = user_id, variant_id=variant_id, reason="Subscription Monthly Renewal create", credit_type="subscription")

    elif event_name == "subscription_updated":
        supabase.from_("subscriptions").update(sub_data).eq("user_id", user_id).execute()
        print("Subscription updated for", user_id)

        # Optional: Add credits if you want on renewals or upgrades
        # await add_credits_to_user(user_id, variant_name, "subscription_updated")

    elif event_name in ["subscription_cancelled", "subscription_expired"]:
        supabase.from_("subscriptions").update({
            "status": "cancelled",
            "ends_at": ends_at
        }).eq("user_id", user_id).execute()

        # Set user as not premium
        supabase.from_("users").update({
            "subscription_status": False
        }).eq("id", user_id).execute()

        print("Subscription cancelled/expired for", user_id)

    elif event_name == "subscription_resumed":
        supabase.from_("subscriptions").update({
            "status": "active",
            "renews_at": renews_at,
            "ends_at": ends_at
        }).eq("user_id", user_id).execute()
        print("Subscription resumed for", user_id)

        # Add credits on resume as well
        await add_credits_to_user(user_id = user_id, variant_id=variant_id, reason="Subscription Monthly Renewal resume", credit_type="subscription")

    # Always update user subscription status
    supabase.from_("users").update({
        "subscription_status": status == "active",
    }).eq("id", user_id).execute()


@router.post("/update-subscription")
async def update_subscription(payload: dict):
    user_id = payload.get("user_id")
    new_variant_id = payload.get("variant_id")
    if not user_id or not new_variant_id:
        raise HTTPException(400, "Missing user_id or variant_id")

    # fetch the existing subscription_id for this user
    resp = supabase.from_("subscriptions") \
        .select("subscription_id") \
        .eq("user_id", user_id) \
        .eq("status", "active") \
        .maybe_single() \
        .execute()
    sub = resp.data
    if not sub:
        raise HTTPException(400, "No active subscription found")

    subscription_id = sub["subscription_id"]

    # PATCH to Lemon Squeezy to change plan
    url = f"https://api.lemonsqueezy.com/v1/subscriptions/{subscription_id}"
    body = {
      "data": {
        "type": "subscriptions",
        "id": subscription_id,
        "attributes": {
          "variant_id": new_variant_id,
          "invoice_immediately": True
        }
      }
    }
    headers = {
      "Authorization": f"Bearer {LEMON_API_KEY}",
      "Accept": "application/vnd.api+json",
      "Content-Type": "application/vnd.api+json"
    }
    async with httpx.AsyncClient() as client:
        r = await client.patch(url, json=body, headers=headers)
        r.raise_for_status()

    # return the webhook will update your DB automatically
    return {"message": "Subscription change initiated"}

def calculate_next_billing_date():
    # You can implement logic for the next billing date. For example, for monthly plans:
    return datetime.utcnow().replace(hour=0, minute=0, second=0) + datetime.timedelta(days=30)     