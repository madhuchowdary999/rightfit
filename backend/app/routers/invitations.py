import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Invitation, Job, Candidate, User, Organization, AuditLog
from ..deps import current_recruiter
from ..services.emailer import send_invite
from ..config import settings

router = APIRouter(prefix="/invitations", tags=["invitations"])

class InviteIn(BaseModel):
    job_id: str
    candidate_email: EmailStr

@router.post("")
def invite(body: InviteIn, db: Session = Depends(get_db), user_id: str = Depends(current_recruiter)):
    job = db.get(Job, body.job_id)
    if not job:
        raise HTTPException(404, "job not found")
    cand = db.query(Candidate).filter(Candidate.email == body.candidate_email.lower()).first()
    if not cand:
        cand = Candidate(email=body.candidate_email.lower())
        db.add(cand)
        db.flush()
    inv = Invitation(job_id=job.id, jd_version=job.jd_version, candidate_id=cand.id,
                     token=secrets.token_urlsafe(32),
                     expires_at=datetime.utcnow() + timedelta(hours=settings.invitation_ttl_hours))
    db.add(inv)
    db.commit()
    link = f"/assess/{inv.token}"
    org = db.get(Organization, job.org_id)
    status = send_invite(db, body.candidate_email, org.name if org else "the recruiter", job.title, link, inv.expires_at.isoformat())
    db.add(AuditLog(actor="system", action=f"invite_email_{status}", entity=f"invitation:{inv.id}"))
    db.commit()
    # single-use link: /assess/{token}
    return {"invitation_id": inv.id, "link": link, "expires_at": inv.expires_at.isoformat(), "email_status": status}
