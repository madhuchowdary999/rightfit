from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Invitation, Assessment, Answer, Job, EvidenceItem, VerificationReport, AuditLog
from ..config import settings
from ..services.questions import generate_questions
from ..services.jd_parser import Requirements
from ..services.evaluation import evaluate

router = APIRouter(prefix="/assessments", tags=["assessments"])

class StartOut(BaseModel):
    assessment_id: str
    questions: list
    max_questions: int

class AnswerIn(BaseModel):
    question_idx: int
    response: str
    evidence_refs: list[str] = []

class SubmitOut(BaseModel):
    report_id: str
    compatibility_score: float
    gaps: list

@router.post("/start/{token}", response_model=StartOut)
def start(token: str, db: Session = Depends(get_db)):
    inv = db.query(Invitation).filter(Invitation.token == token).first()
    if not inv or inv.used or inv.expires_at < datetime.utcnow():
        raise HTTPException(410, "invitation invalid or expired")
    existing = db.query(Assessment).filter(Assessment.invitation_id == inv.id).first()
    if existing:
        return StartOut(assessment_id=existing.id, questions=existing.questions_json,
                        max_questions=settings.max_questions_per_round)
    job = db.get(Job, inv.job_id)
    req = Requirements(**(job.requirements_json or {}))
    ev = db.query(EvidenceItem).filter(EvidenceItem.candidate_id == inv.candidate_id).all()
    tags = [t for e in ev for t in (e.skill_tags or [])]
    qs = generate_questions(req, tags)
    for i, q in enumerate(qs):
        q["idx"] = i
    a = Assessment(invitation_id=inv.id, jd_version=inv.jd_version,
                   questions_json=qs[: settings.max_questions_per_round])
    db.add(a)
    db.commit()
    db.refresh(a)
    return StartOut(assessment_id=a.id, questions=a.questions_json, max_questions=settings.max_questions_per_round)

@router.post("/{assessment_id}/answer")
def submit_answer(assessment_id: str, body: AnswerIn, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(404, "assessment not found")
    if body.question_idx >= settings.max_questions_per_round:
        raise HTTPException(400, "question cap exceeded")
    db.add(Answer(assessment_id=a.id, question_idx=body.question_idx,
                  response=body.response, evidence_refs=body.evidence_refs))
    db.commit()
    return {"ok": True}

@router.post("/{assessment_id}/submit", response_model=SubmitOut)
def submit(assessment_id: str, db: Session = Depends(get_db)):
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(404, "assessment not found")
    inv = db.get(Invitation, a.invitation_id)
    job = db.get(Job, inv.job_id)
    req = Requirements(**(job.requirements_json or {}))
    answers = [{"question_idx": x.question_idx, "response": x.response, "evidence_refs": x.evidence_refs}
               for x in db.query(Answer).filter(Answer.assessment_id == a.id).all()]
    result = evaluate(req, a.questions_json, answers)
    existing = db.query(VerificationReport).filter(VerificationReport.assessment_id == a.id).first()
    if existing:
        existing.compatibility_score = result["compatibility_score"]
        existing.skill_status_json = result["skill_status"]
        existing.gaps_json = result["gaps"]
        db.commit()
        rep = existing
    else:
        rep = VerificationReport(assessment_id=a.id, compatibility_score=result["compatibility_score"],
                                 skill_status_json=result["skill_status"], gaps_json=result["gaps"])
        db.add(rep)
    a.submitted_at = datetime.utcnow()
    inv.used = True  # single-use: token closes after submission
    db.add(AuditLog(actor="system", action="verification_report_generated", entity=f"assessment:{a.id}"))
    db.commit()
    db.refresh(rep)
    return SubmitOut(report_id=rep.id, compatibility_score=rep.compatibility_score, gaps=rep.gaps_json)
