import datetime
from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
import os
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv
from dateutil import parser
from app.utils.billing_functions import process_order_event, process_subscription_event

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
    if product_type == "subscription" and event_name !=  "order_created":
        await process_subscription_event(event_name, payload, user_id)
    elif product_type == "topup":
        await process_order_event(payload, user_id)
    return {"status": "success"}


# @router.post("/update-subscription")
# async def update_subscription(payload: dict):
#     user_id = payload.get("user_id")
#     new_variant_id = payload.get("variant_id")
#     if not user_id or not new_variant_id:
#         raise HTTPException(400, "Missing user_id or variant_id")

#     # fetch the existing subscription_id for this user
#     resp = supabase.from_("subscriptions") \
#         .select("subscription_id") \
#         .eq("user_id", user_id) \
#         .eq("status", "active") \
#         .maybe_single() \
#         .execute()
#     sub = resp.data
#     if not sub:
#         raise HTTPException(400, "No active subscription found")

#     subscription_id = sub["subscription_id"]

#     # PATCH to Lemon Squeezy to change plan
#     url = f"https://api.lemonsqueezy.com/v1/subscriptions/{subscription_id}"
#     body = {
#       "data": {
#         "type": "subscriptions",
#         "id": subscription_id,
#         "attributes": {
#           "variant_id": new_variant_id,
#           "invoice_immediately": True
#         }
#       }
#     }
#     headers = {
#       "Authorization": f"Bearer {LEMON_API_KEY}",
#       "Accept": "application/vnd.api+json",
#       "Content-Type": "application/vnd.api+json"
#     }
#     async with httpx.AsyncClient() as client:
#         r = await client.patch(url, json=body, headers=headers)
#         r.raise_for_status()

#     # return the webhook will update your DB automatically
#     return {"message": "Subscription change initiated"}

