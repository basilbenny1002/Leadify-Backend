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
    x_signature: str = Header(None)  # Capture the signature header
):
    # Read raw request body for signature verification
    raw_body = await request.body()

    # Verify signature
    if not x_signature or not verify_signature(raw_body, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload after verifying signature
    payload = await request.json()
    event_name = payload.get("meta", {}).get("event_name")
    custom_data = payload.get("meta", {}).get("custom_data", {})
    user_id = custom_data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user ID")

    # Process subscription event
    await process_subscription_event(event_name, payload, user_id)

    return {"status": "success"}

async def process_subscription_event(event_name: str, payload: dict, user_id: str):
    print(payload)
    
    data = payload.get("data", {}).get("attributes", {})

    print(data)

    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    subscription_id = data.get("id")  # ID is directly under "data"
    status = attributes.get("status")
    renews_at = attributes.get("renews_at")
    ends_at = attributes.get("ends_at")
    variant_id = attributes.get("variant_id")

     # Check existing subscription for user
    existing = supabase.table("subscriptions").select("*").eq("user_id", user_id).maybe_single().execute()

    sub_data = {
        "user_id": user_id,
        "subscription_id": subscription_id,
        "status": status,
        "renews_at": renews_at,
        "ends_at": ends_at,
        "plan_id": variant_id,
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

    elif event_name in ["subscription_cancelled", "subscription_expired"]:
        supabase.table("subscriptions").update({
            "status": "cancelled",
            "ends_at": ends_at
        }).eq("user_id", user_id).execute()

        print("Subscription cancelled/expired for", user_id)

    elif event_name == "subscription_resumed":
        supabase.table("subscriptions").update({
            "status": "active",
            "renews_at": renews_at,
            "ends_at": ends_at
        }).eq("user_id", user_id).execute()

        print("Subscription resumed for", user_id)

    # In all cases, update the user table to match
    supabase.table("users").update({
        "plan_id": variant_id,
        "subscription_status": status if status else "cancelled"
    }).eq("id", user_id).execute()