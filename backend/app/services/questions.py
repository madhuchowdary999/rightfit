"""Question generation: job-specific, gap-targeted, capped at 5 per round (locked rule).
LLM path when a provider is configured; deterministic fallback otherwise."""
from .jd_parser import Requirements
from .llm import get_adapter
from ..config import settings

QUESTION_TEMPLATES = {
    "gap": ("Describe one specific task where you used {skill} end to end: what you built, "
            "your exact role in it, and one measurable outcome."),
    "depth": ("Walk through how you applied {skill} in your most recent project and what you personally owned."),
}

def _normalize(tags):
    return {t.strip().lower() for t in tags or []}

def generate_questions(requirements: Requirements, evidence_tags: list[str]) -> list[dict]:
    adapter = get_adapter()
    if adapter is not None:
        try:
            qs = adapter.generate_questions(requirements.model_dump(), evidence_tags, settings.max_questions_per_round)
            return qs[: settings.max_questions_per_round]
        except Exception:
            pass
    ev = _normalize(evidence_tags)
    must = [s for s in requirements.must_have if s]
    gaps = [s for s in must if s.lower() not in ev]
    covered = [s for s in must if s.lower() in ev]
    out = []
    for s in gaps:
        out.append({"skill": s, "kind": "gap", "text": QUESTION_TEMPLATES["gap"].format(skill=s)})
    for s in covered:
        if len(out) >= settings.max_questions_per_round:
            break
        out.append({"skill": s, "kind": "depth", "text": QUESTION_TEMPLATES["depth"].format(skill=s)})
    return out[: settings.max_questions_per_round]
