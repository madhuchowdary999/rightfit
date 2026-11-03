from fastapi import Header, HTTPException
from .services.security import verify

def current_recruiter(authorization: str = Header(default="")) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "sign in required")
    payload = verify(authorization[len("Bearer "):])
    if not payload:
        raise HTTPException(401, "session expired, sign in again")
    return payload["sub"]
