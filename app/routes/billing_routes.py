from fastapi import FastAPI, HTTPException, Depends, Request
import httpx
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends, Header, HTTPException
import jwt
import os
from supabase import create_client, Client
from app.utils.billing_functions import calculate_proration_logic, cancel_subscription_logic, deduct_credits, fetch_invoices_logic
from app.utils.authorization import verify_jwt
import uuid

class RevealRequest(BaseModel):
    streamer_id: str

# SUPABASE_SECRET = os.getenv("JWT_SUPABASE_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
LEMON_API_KEY = os.getenv("LEMON_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



router = APIRouter()

@router.post("/subscription/calculate-proration")
async def calculate_proration_route(request: Request, user=Depends(verify_jwt)):
    data = await request.json()
    new_plan_id = data.get("planId")
    is_yearly = data.get("isYearly")

    if not new_plan_id:
        raise HTTPException(400, "Missing planId")

    proration_amount = await calculate_proration_logic(user["sub"], new_plan_id, is_yearly)
    return {"prorationAmount": proration_amount}

@router.post("/subscription/cancel")
async def cancel_subscription(user=Depends(verify_jwt)):
    user_id = user["sub"]
    return await cancel_subscription_logic(user_id)

@router.get("/subscription/customer-portal")
async def get_customer_portal(user_id = Depends(verify_jwt)):
    response = await supabase.table("users").select("lemon_customer_id").eq("id", user_id).single().execute()

    customer_id = response.data.get("lemon_customer_id")


    if not customer_id:
            raise HTTPException(status_code=404, detail="Customer ID not found")
    
    # Call LemonSqueezy to get portal link
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.lemonsqueezy.com/v1/customer-portal",
            headers={
                "Authorization": f"Bearer {LEMON_API_KEY}",
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/json",
            },
            json={"customer_id": customer_id},
        )

        if response.status_code == 201:
            return response.json()["data"]["attributes"]
        
        else:
            raise HTTPException(status_code=500, detail="Failed to create customer portal")

# def get_current_user_id(authorization: str = Header(...)):
#     token = authorization.split(" ")[1]
#     payload = jwt.decode(token, SUPABASE_SECRET, algorithms=["HS256"])
#     return payload['sub']  # supabase user_id is in sub claim

@router.post("/buy-credits")
async def buy_credits(
    request: Request,
    supabase_user: dict = Depends(verify_jwt)
):
    body = await request.json()
    credits_to_add = body.get("credits")

    if not credits_to_add or not isinstance(credits_to_add, int):
        raise HTTPException(status_code=400, detail="Missing or invalid credits")

    user_id = supabase_user["sub"]

    # 1. Add credits to the user's balance
    update_response = supabase.table("users").update({
        "credits": f"credits + {credits_to_add}"
    }).eq("id", user_id).execute()

    if update_response.get("error"):
        raise HTTPException(status_code=500, detail="Failed to update credits")

    # 2. Log the credit transaction
    transaction_id = str(uuid.uuid4())

    transaction_data = {
        "id": transaction_id,
        "user_id": user_id,
        "credits": credits_to_add,
        "type": "topup",
        "action": "manual_purchase",
        "amount": credits_to_add,
    }

    txn_response = supabase.from_("credit_transactions").insert(transaction_data).execute()

    if txn_response.get("error"):
        raise HTTPException(status_code=500, detail="Failed to log transaction")

    return {"success": True, "message": "Credits added and transaction logged"}

@router.post("/reveal-socials")
async def reveal_socials(
    payload: RevealRequest,
    userId: dict = Depends(verify_jwt),
):
    print(userId)
    print(payload)
    streamer_id = payload.streamer_id

    try:
        # Deduct credits for revealing socials
        await deduct_credits(userId, "reveal_socials")
        print("Credits deducted")
        # Update the socials_revealed column for this user + streamer
        supabase.from_("twitch_streamers") \
                .update({"socials_revealed": True}) \
                .eq("id", streamer_id) \
                .eq("user_id", userId) \
                .execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success", "message": "Social links revealed"}

@router.post("/reveal-email")
async def reveal_email(
    payload: RevealRequest,
    userId: dict = Depends(verify_jwt),
):
    streamer_id = payload.streamer_id

    try:
        # Deduct credits for revealing email
        await deduct_credits(userId, "reveal_email")

        # Update the email_revealed column for this user + streamer
        supabase.table("twitch_streamers") \
            .update({"email_revealed": True}) \
            .eq("id", streamer_id) \
            .eq("user_id", userId) \
            .execute()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success", "message": "Email revealed"}