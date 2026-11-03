import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base
from sqlalchemy import Column, String, Text, DateTime

def uid() -> str:
    return uuid.uuid4().hex

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="recruiter")  # recruiter | admin

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    title: Mapped[str] = mapped_column(String(200))
    jd_text: Mapped[str] = mapped_column(Text)
    jd_version: Mapped[int] = mapped_column(Integer, default=1)
    requirements_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # parsed: must_have, nice_to_have, seniority, domain

class Candidate(Base):
    __tablename__ = "candidates"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(320), index=True)
    account_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)  # optional Skills Passport account

class Invitation(Base):
    __tablename__ = "invitations"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"))
    jd_version: Mapped[int] = mapped_column(Integer)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"))
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used: Mapped[bool] = mapped_column(Boolean, default=False)

class EvidenceItem(Base):
    __tablename__ = "evidence_items"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"))
    type: Mapped[str] = mapped_column(String(40))   # certification | verified_task | artifact | reference
    source: Mapped[str] = mapped_column(String(500))
    skill_tags: Mapped[list] = mapped_column(JSON, default=list)

class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    invitation_id: Mapped[str] = mapped_column(ForeignKey("invitations.id"))
    jd_version: Mapped[int] = mapped_column(Integer)
    questions_json: Mapped[list] = mapped_column(JSON)  # max 5 per locked rule
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"))
    question_idx: Mapped[int] = mapped_column(Integer)
    response: Mapped[str] = mapped_column(Text)
    evidence_refs: Mapped[list] = mapped_column(JSON, default=list)

class VerificationReport(Base):
    __tablename__ = "verification_reports"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"), unique=True)
    compatibility_score: Mapped[float] = mapped_column()
    skill_status_json: Mapped[dict] = mapped_column(JSON)  # per-skill: verified | gap | unverified, with evidence refs
    gaps_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    actor: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    entity: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EmailOutbox(Base):
    __tablename__ = "email_outbox"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    to_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String, default="queued_no_smtp")
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
