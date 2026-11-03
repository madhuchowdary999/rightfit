import csv, io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import VerificationReport

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{assessment_id}")
def get_report(assessment_id: str, db: Session = Depends(get_db)):
    r = db.query(VerificationReport).filter(VerificationReport.assessment_id == assessment_id).first()
    if not r:
        raise HTTPException(404, "report not ready")
    return {"compatibility_score": r.compatibility_score, "skill_status": r.skill_status_json, "gaps": r.gaps_json}

@router.get("/{assessment_id}/export.csv")
def export_csv(assessment_id: str, db: Session = Depends(get_db)):
    r = db.query(VerificationReport).filter(VerificationReport.assessment_id == assessment_id).first()
    if not r:
        raise HTTPException(404, "report not ready")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["skill", "status", "evidence_refs"])
    for skill, st in (r.skill_status_json or {}).items():
        w.writerow([skill, st.get("status"), ";".join(st.get("evidence_refs", []))])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename=verification_{assessment_id}.csv"})
