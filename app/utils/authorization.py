import jwt
from fastapi import Depends, HTTPException, Request
import os
from dotenv import load_dotenv

load_dotenv() 
SUPABASE_JWT_SECRET = os.getenv("JWT_SUPABASE_SECRET")
if not SUPABASE_JWT_SECRET:
    raise RuntimeError("JWT_SUPABASE_SECRET environment variable is not set")
def verify_jwt(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth.split(" ")[1]
    payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated",issuer="https://rrexykfszwdetlvfmuxd.supabase.co/auth/v1")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload['sub']