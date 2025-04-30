import datetime
from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
import os
from supabase import create_client, Client

router = APIRouter()

# Supabase init
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
LEMON_SECRET = os.getenv("LEMON_WEBHOOK_SECRET")

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

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user ID")

    await process_subscription_event(event_name, payload, user_id)
    return {"status": "success"}

async def process_subscription_event(event_name: str, payload: dict, user_id: str):
    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    subscription_id = data.get("id")
    status = attributes.get("status")
    renews_at = attributes.get("renews_at")
    ends_at = attributes.get("ends_at")
    variant_id = attributes.get("variant_id")
    variant_name = attributes.get("variant_name")
    product_id = attributes.get("product_id")
    product_name = attributes.get("product_name")
    billing_anchor = attributes.get("billing_anchor")
    created_at = attributes.get("created_at")
    card_brand = attributes.get("card_brand")
    card_last_four = attributes.get("card_last_four")

    # Check for existing subscription
    existing = supabase.table("subscriptions").select("*").eq("user_id", user_id).maybe_single().execute()

    sub_data = {
        "user_id": user_id,
        "subscription_id": subscription_id,
        "status": status,
        "renews_at": renews_at,
        "ends_at": ends_at,
        "plan_id": variant_id,
        "plan_name": variant_name,
        "product_id": product_id,
        "product_name": product_name,
        "billing_anchor": billing_anchor,
        "created_at": created_at,
        "card_brand": card_brand,
        "card_last_four": card_last_four
    }

    if event_name == "subscription_created":
        if existing and existing.data:
            supabase.table("subscriptions").update(sub_data).eq("user_id", user_id).execute()
        else:
            supabase.table("subscriptions").insert(sub_data).execute()
        print("Subscription created by", user_id)

    elif event_name == "subscription_updated":
        supabase.table("subscriptions").update(sub_data).eq("user_id", user_id).execute()
        print("Subscription updated for", user_id)

    # elif event_name in ["subscription_cancelled", "subscription_expired"]:
    #     supabase.table("subscriptions").update({
    #         "status": "cancelled",
    #         "ends_at": ends_at
    #     }).eq("user_id", user_id).execute()
    #     print("Subscription cancelled/expired for", user_id)

    # elif event_name == "subscription_resumed":
    #     supabase.table("subscriptions").update({
    #         "status": "active",
    #         "renews_at": renews_at,
    #         "ends_at": ends_at
    #     }).eq("user_id", user_id).execute()
    #     print("Subscription resumed for", user_id)

    # Always update users table
    supabase.table("users").update({
        "subscription_status": True if status else False,
    }).eq("id", user_id).execute()


@router.post("/update-subscription")
async def update_subscription(request: Request):
    # Get the user ID and the new plan ID from the request
    body = await request.json()
    user_id = body.get("user_id")
    new_plan_id = body.get("new_plan_id")

    # Check if the user has an active subscription
    user_subscription = supabase.table("subscriptions").select("*").eq("user_id", user_id).eq("status", "active").maybe_single().execute()

    if not user_subscription or not user_subscription.data:
        raise HTTPException(status_code=400, detail="No active subscription found for this user.")

    current_subscription = user_subscription.data
    current_plan_id = current_subscription["plan_id"]

    # If the current plan is the same as the new plan, return an error (to prevent unnecessary re-activation)
    if current_plan_id == new_plan_id:
        raise HTTPException(status_code=400, detail="You already have this plan.")

    # Now we need to decide whether it's an upgrade or downgrade
    if new_plan_id != "free":
        # Cancel the current subscription (keep the current_period_end and status, etc., depending on the situation)
        supabase.table("subscriptions").update({
            "status": "cancelled",
            "ends_at": datetime.utcnow()  # You might need to adjust this if you want the cancellation to take effect in the future
        }).eq("user_id", user_id).eq("status", "active").execute()

        # Now create a new subscription with the new plan
        new_subscription_data = {
            "user_id": user_id,
            "plan_id": new_plan_id,
            "status": "active",  # Set new status to active
            "current_period_start": datetime.utcnow(),
            "current_period_end": calculate_next_billing_date(),  # Assuming you want to calculate the next billing date
            "is_active": True
        }

        supabase.table("subscriptions").insert([new_subscription_data]).execute()
        return {"message": "Subscription updated successfully."}
    
    else:
        # If the user wants to downgrade to the free plan
        # Cancel the current active subscription
        supabase.table("subscriptions").update({
            "status": "cancelled",
            "ends_at": datetime.utcnow()
        }).eq("user_id", user_id).eq("status", "active").execute()

        # Set the user to the free plan (no need to handle payments for the free plan)
        free_subscription_data = {
            "user_id": user_id,
            "plan_id": "free",
            "status": "free",  # Mark it as free
            "current_period_start": datetime.utcnow(),
            "current_period_end": None,  # No end date for free plan
            "is_active": True
        }

        supabase.table("subscriptions").insert([free_subscription_data]).execute()
        return {"message": "User downgraded to the free plan."}

def calculate_next_billing_date():
    # You can implement logic for the next billing date. For example, for monthly plans:
    return datetime.utcnow().replace(hour=0, minute=0, second=0) + datetime.timedelta(days=30)