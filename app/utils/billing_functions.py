import os
from typing import Optional
from fastapi import HTTPException
import httpx
from supabase import create_client, Client
from datetime import datetime, timezone
from dateutil import parser
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

CREDIT_COSTS = {
    "reveal_socials": 1,
    "reveal_email": 2,
    "export_json": 3,
    "export_excel": 5,
    "search": 1
}

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
LEMON_API_KEY = os.getenv("LEMON_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def process_order_event(payload: str, user_id: dict):
    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    variant_id = attributes.get("first_order_item", {}).get("variant_id")
    # variant_name = attributes.get("first_order_item", {}).get("variant_name", "Unknown Pack")
    order_id = data.get("id")

    print(variant_id)

    customer_relationship = data.get("relationships", {}).get("customer", {})
    customer_id = customer_relationship.get("data", {}).get("id")

    # Add credits based on the credit pack variant
    await add_credits(user_id=user_id, variant_id=variant_id,reason="Credit Pack Purchase", credit_type="topup")
    
    print("Credits added")

    # 🧠 Update user in Supabase with LemonSqueezy customer ID
    if customer_id:
        try:
            response = supabase.table("users").update({
                "lemon_customer_id": customer_id
            }).eq("id", user_id).execute()

            print(response)
            print(f"Customer ID {customer_id} saved to user {user_id}")
        except Exception as e:
            print(f"Failed to update user with customer ID: {e}")

    print(f"Credits added for user {user_id} from order {order_id}")

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

async def process_subscription_event(event_name: str, payload: dict, user_id: str):
    data = payload.get("data", {})
    print("DATA PRINT")
    print(data)
    attributes = data.get("attributes", {})
    print("ATTRIBUTES PRINT")
    print(attributes)
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

    print("variant name : ")
    print(variant_name)

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

        customer_id = attributes.get("customer_id")
        if customer_id:
            supabase.from_("users").update({
                "lemon_customer_id": customer_id
            }).eq("id", user_id).execute()
            print(f"Stored customer_id {customer_id} for user {user_id}")

        # Add credits on new subscription
        await add_credits(user_id = user_id, variant_id=variant_id, reason="Subscription Monthly Renewal create", credit_type="subscription")

    elif event_name == "subscription_updated":
        supabase.from_("subscriptions").update(sub_data).eq("user_id", user_id).execute()
        print("Subscription updated for", user_id)

        # Optional: Add credits if you want on renewals or upgrades
        # await add_credits(user_id, variant_name, "subscription_updated")

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
        await add_credits(user_id = user_id, variant_id=variant_id, reason="Subscription Monthly Renewal resume", credit_type="subscription")

    # Always update user subscription status
    supabase.from_("users").update({
        "subscription_plan": get_plan_name(variant_name),
        "subscription_status": status == "active",
    }).eq("id", user_id).execute()

async def add_credits(
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

    new_credits = int(current_credits) + int(credits)
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

    if not insert_response:
        print(insert_response)
        raise HTTPException(500, detail="Failed to log credit transaction.")

    print(f"✅ Added {credits} credits to user {user_id} | Reason: {reason} | Type: {credit_type}")

async def deduct_credits(user_id: str, action: str):
    cost = CREDIT_COSTS.get(action)
    if cost is None:
        raise ValueError("Invalid action type")
    

    user = supabase.from_("users").select("credits").eq("id", user_id).single().execute()
    if  user.data is None:
        raise Exception("User not found")

    current_credits = user.data["credits"]
    if current_credits < cost:
        raise Exception("Insufficient credits")
    

    updated = supabase.from_("users").update({
        "credits": current_credits - cost
    }).eq("id", user_id).execute()


    if not updated:
        raise Exception("Failed to deduct credits")
    
    supabase.from_("credit_usage_logs").insert({
            "user_id": user_id,
            "action": action,
            "credits_used": cost,
        }).execute()

    print(f"✅ Deducted {cost} credits from user {user_id} | Action: {action}")

    return True

def get_plan_name(full_plan: str) -> str:
    return full_plan.split(" ")[0]

def calculate_next_billing_date():
    # You can implement logic for the next billing date. For example, for monthly plans:
    return datetime.now(datetime.timezone.utc).replace(hour=0, minute=0, second=0) + datetime.timedelta(days=30)     

def get_plan_duration_days(is_yearly: bool):
    return 365 if is_yearly else 30

async def calculate_proration_logic(user_id: str, new_plan_id: int, is_yearly: bool):
    # Fetch current subscription info
    resp = supabase.from_("subscriptions").select("*").eq("user_id", user_id).maybe_single().execute()
    subscription = resp.data
    if not subscription:
        raise HTTPException(404, "Subscription not found")

    current_variant_id = subscription["plan_id"]
    renews_at_str = subscription["renews_at"]
    if not renews_at_str:
        return VARIANT_CREDIT_MAP.get(new_plan_id)

    renews_at = parser.parse(renews_at_str)
    now = datetime.now(timezone.utc)

    days_remaining = (renews_at - now).days
    if days_remaining < 0:
        return VARIANT_CREDIT_MAP.get(new_plan_id)

    current_price = VARIANT_CREDIT_MAP.get(current_variant_id)
    new_price = VARIANT_CREDIT_MAP.get(int(new_plan_id))

    if not current_price or not new_price:
        raise HTTPException(400, "Unknown plan ID")

    total_days = get_plan_duration_days(is_yearly)
    credit = (current_price / total_days) * days_remaining
    prorated_amount = round(new_price - credit, 2)

    return max(prorated_amount, 0)

async def cancel_subscription_logic(user_id: str):
    # Get subscription ID
    sub = supabase.from_("subscriptions").select("subscription_id").eq("user_id", user_id).maybe_single().execute()
    if not sub or not sub.data:
        raise HTTPException(404, "No active subscription found")

    subscription_id = sub.data["subscription_id"]

    url = f"https://api.lemonsqueezy.com/v1/subscriptions/{subscription_id}"
    body = {
        "data": {
            "type": "subscriptions",
            "id": subscription_id,
            "attributes": {
                "cancelled": True
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {LEMON_API_KEY}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json"
    }

    async with httpx.AsyncClient() as client:
        res = await client.patch(url, json=body, headers=headers)
        res.raise_for_status()

    return {"message": "Subscription cancelled"}

async def fetch_invoices_logic(user_id: str):
    # Get subscription to access Lemon ID
    sub = supabase.from_("subscriptions").select("subscription_id").eq("user_id", user_id).maybe_single().execute()
    if not sub or not sub.data:
        return []

    subscription_id = sub.data["subscription_id"]

    url = f"https://api.lemonsqueezy.com/v1/subscriptions/{subscription_id}/invoices"

    headers = {
        "Authorization": f"Bearer {LEMON_API_KEY}",
        "Accept": "application/vnd.api+json"
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        invoices = res.json()

    # Optional: format nicely
    formatted = [
        {
            "id": inv["id"],
            "amount": inv["attributes"]["total"],
            "status": inv["attributes"]["status"],
            "paid_at": inv["attributes"]["paid_at"],
            "url": inv["attributes"]["urls"]["invoice_url"]
        }
        for inv in invoices.get("data", [])
    ]

    return formatted