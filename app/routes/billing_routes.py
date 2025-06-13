from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends, Header, HTTPException
import jwt
import os
from supabase import create_client, Client
from utils.authorization import verify_jwt
import uuid

SUPABASE_SECRET = os.getenv("JWT_SUPABASE_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ACTION_COSTS = {
    "streamer_search": 1,
    "reveal_social_links": 1,
    "reveal_email": 2,
}


router = APIRouter()

def get_current_user_id(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    payload = jwt.decode(token, SUPABASE_SECRET, algorithms=["HS256"])
    return payload['sub']  # supabase user_id is in sub claim

class UseCreditsRequest(BaseModel):
    action: str

@router.post("/use-credits")
def use_credits(data: UseCreditsRequest, user_id: str = Depends(get_current_user_id)):
    action = data.action

    if action not in ACTION_COSTS:
        raise HTTPException(400, detail="Invalid action.")

    cost = ACTION_COSTS[action]

    # Get user
    response = supabase.from_("users").select("*").eq("id", user_id).single().execute()
    user = response.data

    if not user:
        raise HTTPException(404, detail="User not found.")

    if user["credits"] < cost:
        raise HTTPException(400, detail="Insufficient credits.")

    # Deduct credits
    new_credits = user["credits"] - cost
    update_response = supabase.from_("users").update({"credits": new_credits}).eq("id", user_id).execute()

    if update_response.status_code >= 400:
        raise HTTPException(500, detail="Failed to update credits.")

    # Insert credit transaction
    transaction = {
        "user_id": user_id,
        "type": "usage",
        "action": action,
        "amount": cost,
        "created_at": datetime.now(datetime.timezone.utc).isoformat()
    }

    insert_response = supabase.from_("credit_transactions").insert(transaction).execute()

    if insert_response.status_code >= 400:
        raise HTTPException(500, detail="Failed to record transaction.")

    return {
        "success": True,
        "remaining_credits": new_credits
    }


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