"""Evaluation v0 (deterministic): evidence-first scoring.
- A must-have skill covered by candidate evidence -> verified, citing the evidence.
- An answered gap question with evidence refs -> verified for that skill.
- Answered without evidence -> unverified (honest label, never fake-verified).
- Unanswered -> gap.
LLM-based evaluation swaps in behind the same interface in M3."""
import re
from .jd_parser import Requirements

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def evaluate(requirements: Requirements, questions: list[dict], answers: list[dict]) -> dict:
    skill_status: dict[str, dict] = {}
    # evidence-covered skills first
    for a in answers:
        refs = a.get("evidence_refs") or []
        q = next((q for q in questions if q.get("idx") == a.get("question_idx")), None)
        if not q:
            continue
        skill = q["skill"]
        text = a.get("response") or ""
        if refs and _norm(text):
            skill_status[skill] = {"status": "verified", "evidence_refs": refs, "question_idx": q["idx"]}
        elif _norm(text):
            skill_status[skill] = {"status": "unverified", "evidence_refs": [], "question_idx": q["idx"]}
        else:
            skill_status[skill] = {"status": "gap", "evidence_refs": [], "question_idx": q["idx"]}
    for s in requirements.must_have:
        if s.lower() not in {k.lower() for k in skill_status}:
            skill_status[s] = {"status": "gap", "evidence_refs": [], "question_idx": None}
    must = [s for s in requirements.must_have if s] or list(skill_status.keys())
    verified = sum(1 for s in must if skill_status.get(s, {}).get("status") == "verified")
    compatibility = round(100.0 * verified / len(must), 1) if must else 0.0
    gaps = [s for s in must if skill_status.get(s, {}).get("status") != "verified"]
    return {"compatibility_score": compatibility, "skill_status": skill_status, "gaps": gaps}
