import os
from typing import Optional
from fastapi import HTTPException
from supabase import create_client, Client
from datetime import datetime, timezone

# Credit mapping based on LemonSqueezy variant_id
VARIANT_CREDIT_MAP = {
    # Top-up Packs
    838117: 100,   # Starter
    838118: 500,   # Growth
    838119: 1000,  # Scale
    838121: 5000,  # Power

    # Subscriptions
    783425: 150,   # Basic Monthly
    783451: 150,   # Basic Yearly
    783455: 500,   # Pro Monthly
    783457: 500,   # Pro Yearly
}

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
async def add_credits_to_user(
    user_id: str,
    reason: str,
    credits: Optional[int] = None,
    variant_id: Optional[int] = None,
    credit_type: str = "topup"):
    # Auto resolve credits from variant_id if credits not manually passed
    print(credits)
    print(variant_id)
    print(reason)
    print(credit_type)
    if credits is None:
        if variant_id is None:
            raise ValueError("Either 'credits' or 'variant_id' must be provided.")
        credits = VARIANT_CREDIT_MAP.get(variant_id)
        if credits is None:
            raise ValueError(f"No credit mapping found for variant ID {variant_id}.")


    # Atomic credit update

    user_response = supabase.from_("users").select("credits").eq("id", user_id).single().execute()

    if not user_response:
        print(user_response)
        raise HTTPException(500, detail="Failed to fetch user's current credits.")

    current_credits = user_response.data["credits"] or 0

    new_credits = current_credits + credits 
    print(current_credits)
    print(credits)
    print(new_credits)
    update_response = supabase.from_("users").update({
        "credits": new_credits
    }).eq("id", user_id).execute()

    if not update_response:
        print(update_response)
        raise HTTPException(500, detail="Failed to update user's credits.")

    print(update_response)

    if not update_response:
        print(update_response)
        raise HTTPException(500, detail="Failed to update credits.")

    # Log the credit transaction
    insert_response = supabase.from_("credit_transactions").insert({
        "user_id": user_id,
        "amount": credits,
        "action": reason,
        "type": credit_type,
        "created_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    print(insert_response)

    if insert_response.status_code >= 400:
        print(insert_response.error)
        raise HTTPException(500, detail="Failed to log credit transaction.")

    print(f"✅ Added {credits} credits to user {user_id} | Reason: {reason} | Type: {credit_type}")

async def process_order_event(payload: str, user_id: dict):
    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    variant_id = attributes.get("first_order_item", {}).get("variant_id")
    variant_name = attributes.get("first_order_item", {}).get("variant_name", "Unknown Pack")
    order_id = data.get("id")
    paid_at = attributes.get("paid_at")
    total = attributes.get("total")
    currency = attributes.get("currency")

    print(variant_id)

    # Add credits based on the credit pack variant
    await add_credits_to_user(user_id=user_id, variant_id=variant_id,reason="Credit Pack Purchase", credit_type="topup")

    # # Optional: Store order info
    # supabase.table("orders").insert({
    #     "user_id": user_id,
    #     "order_id": order_id,
    #     "variant_id": variant_id,
    #     "variant_name": variant_name,
    #     "paid_at": paid_at,
    #     "total": total,
    #     "currency": currency
    # }).execute()

    print(f"Credits added for user {user_id} from order {order_id}")