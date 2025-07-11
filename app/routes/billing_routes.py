from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends, Header, HTTPException
import jwt
import os
from supabase import create_client, Client
from app.utils.billing_functions import deduct_credits
from app.utils.authorization import verify_jwt
import uuid

class RevealRequest(BaseModel):
    streamer_id: str

# SUPABASE_SECRET = os.getenv("JWT_SUPABASE_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



router = APIRouter()

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