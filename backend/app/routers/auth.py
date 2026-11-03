from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..db import get_db
from ..models import Organization, User
from ..services.security import issue

router = APIRouter(prefix="/auth", tags=["auth"])
pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class SignupIn(BaseModel):
    org_name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(body: SignupIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email.lower()).first():
        raise HTTPException(409, "email already registered")
    org = Organization(name=body.org_name)
    db.add(org)
    db.flush()
    user = User(org_id=org.id, email=body.email.lower(), hashed_password=pwd.hash(body.password), role="admin")
    db.add(user)
    db.commit()
    return {"org_id": org.id, "user_id": user.id}

@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not pwd.verify(body.password, user.hashed_password):
        raise HTTPException(401, "wrong email or password")
    return {"access_token": issue(user.id), "user_id": user.id, "org_id": user.org_id}
