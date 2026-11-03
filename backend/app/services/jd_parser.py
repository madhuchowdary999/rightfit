"""JD parsing: extract structured requirements from a job description.
LLM path when a provider is configured; deterministic fallback otherwise.
Output is a DRAFT the recruiter reviews and corrects before inviting candidates."""
from pydantic import BaseModel
from .llm import get_adapter

class Requirements(BaseModel):
    must_have: list[str] = []
    nice_to_have: list[str] = []
    seniority: str | None = None
    domain: str | None = None

SKILL_HINTS = [
    "python", "sql", "snowflake", "airflow", "dbt", "aws", "azure", "gcp",
    "react", "typescript", "javascript", "java", "kafka", "spark", "docker",
    "kubernetes", "terraform", "power bi", "tableau", "etl", "elt", "salesforce",
]

def heuristic_parse(jd_text: str) -> Requirements:
    low = jd_text.lower()
    must = [s for s in SKILL_HINTS if s in low]
    seniority = None
    for level in ("senior", "staff", "principal", "lead", "junior", "mid"):
        if level in low:
            seniority = level
            break
    return Requirements(must_have=must, seniority=seniority)

def parse_jd(jd_text: str) -> Requirements:
    adapter = get_adapter()
    if adapter is not None:
        try:
            return Requirements(**adapter.parse_jd(jd_text))
        except Exception:
            pass  # network/model hiccup: fall back so the recruiter flow never blocks
    return heuristic_parse(jd_text)
