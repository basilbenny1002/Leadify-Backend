import os
from fastapi import HTTPException
from supabase import create_client, Client
from datetime import datetime, timezone

# Map LemonSqueezy variant IDs or plan names to credits based on your Leadify Pricing Model
PLAN_DEFAULT_CREDITS = {
    "free": 25,
    "basic": 150,
    "pro": 500,
}

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
async def add_credits_to_user(user_id: str, plan_name: str, reason: str):
    credits = PLAN_DEFAULT_CREDITS.get(plan_name.lower())
    if credits is None:
        print(f"No credit mapping for plan {plan_name}")
        return


    # Add credits atomically (assuming supabase client supports raw SQL update or equivalent)
    update_response = supabase.table("users").update({
        "credits": f"credits + {credits}"
    }).eq("id", user_id).execute()

    if update_response.status_code >= 400:
        print(update_response.error)
        raise HTTPException(500, detail="Failed to update credits.")

    # Log the credit transaction
    insert_response = supabase.table("credit_transactions").insert({
        "user_id": user_id,
        "amount": credits,
        "action": reason,
        "created_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    if insert_response.status_code >= 400:
        print(insert_response.error)
        raise HTTPException(500, detail="Failed to log credit transaction.")

    print(f"Added {credits} credits to user {user_id} for {reason}.")

async def process_order_event(payload: str, user_id: dict):
    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    variant_id = attributes.get("first_order_item", {}).get("variant_id")
    variant_name = attributes.get("first_order_item", {}).get("variant_name", "Unknown Pack")
    order_id = data.get("id")
    paid_at = attributes.get("paid_at")
    total = attributes.get("total")
    currency = attributes.get("currency")

    # Add credits based on the credit pack variant
    await add_credits_to_user(user_id, variant_name, "credit_pack")

    # Optional: Store order info
    supabase.table("orders").insert({
        "user_id": user_id,
        "order_id": order_id,
        "variant_id": variant_id,
        "variant_name": variant_name,
        "paid_at": paid_at,
        "total": total,
        "currency": currency
    }).execute()

    print(f"Credits added for user {user_id} from order {order_id}")