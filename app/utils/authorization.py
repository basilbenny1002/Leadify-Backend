import jwt
from fastapi import Depends, HTTPException, Request
import os

SUPABASE_JWT_SECRET = os.getenv("JWT_SUPABASE_SECRET")

def verify_jwt(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth.split(" ")[1]
    payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
    return payload