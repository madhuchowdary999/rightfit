from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Job, User
from ..deps import current_recruiter
from ..services.jd_parser import parse_jd

router = APIRouter(prefix="/jobs", tags=["jobs"])

class JobIn(BaseModel):
    org_id: str | None = None
    title: str
    jd_text: str

class JobOut(BaseModel):
    id: str
    title: str
    jd_text: str
    jd_version: int
    requirements_json: dict | None

    class Config:
        from_attributes = True

@router.post("", response_model=JobOut)
def create_job(body: JobIn, db: Session = Depends(get_db), user_id: str = Depends(current_recruiter)):
    org_id = body.org_id or db.get(User, user_id).org_id
    draft = parse_jd(body.jd_text)  # draft the recruiter reviews and corrects
    job = Job(org_id=org_id, title=body.title, jd_text=body.jd_text,
              requirements_json=draft.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.put("/{job_id}/jd", response_model=JobOut)
def update_jd(job_id: str, jd_text: str, db: Session = Depends(get_db), user_id: str = Depends(current_recruiter)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "job not found")
    job.jd_text = jd_text
    job.jd_version += 1          # new version; existing cases keep the old one, flagged
    job.requirements_json = parse_jd(jd_text).model_dump()
    db.commit()
    db.refresh(job)
    return job

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return job
