"""Recruiter session tokens: HMAC-signed, stdlib only, secret from config."""
import base64, hashlib, hmac, json, time
from ..config import settings

def _sign(data: bytes) -> str:
    return base64.urlsafe_b64encode(hmac.new(settings.jwt_secret.encode(), data, hashlib.sha256).digest()).rstrip(b"=").decode()

def issue(user_id: str) -> str:
    body = base64.urlsafe_b64encode(json.dumps({"sub": user_id, "exp": int(time.time()) + settings.access_token_expire_minutes * 60}).encode()).rstrip(b"=").decode()
    return f"{body}.{_sign(body.encode())}"

def verify(token: str) -> dict | None:
    try:
        body, sig = token.split(".")
        if not hmac.compare_digest(sig, _sign(body.encode())):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        return payload if payload.get("exp", 0) >= time.time() else None
    except Exception:
        return None

def current_recruiter(authorization: str = "") -> str:
    from fastapi import Header, HTTPException
    raise RuntimeError  # replaced below; see deps.py
