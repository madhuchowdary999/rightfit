"""Provider-agnostic LLM adapter. One interface, model chosen per task.
Prompts live here, versioned, so behavior is reproducible. The API key arrives
through env only (never committed). If no key is configured, callers fall back
to the deterministic parser so the app always runs."""
import json, re, urllib.request
from ..config import settings

PROMPT_JD_PARSE_V1 = (
    "You extract hiring requirements from job descriptions. "
    "Return ONLY valid JSON, no markdown, with exactly these keys: "
    '{"must_have": [skill strings], "nice_to_have": [skill strings], '
    '"seniority": "junior|mid|senior|staff|principal|lead|null", "domain": "short domain string|null"}. '
    "Be conservative: only list skills the text clearly requires. Job description:\n\n"
)

class GeminiRESTAdapter:
    def _generate(self, prompt: str) -> str:
        url = f"{settings.llm_base_url}/models/{settings.llm_model}:generateContent?key={settings.llm_api_key}"
        payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode())
        return body["candidates"][0]["content"]["parts"][0]["text"]

    def _json(self, prompt: str) -> dict:
        text = self._generate(prompt)
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise ValueError("no JSON in model output")
        return json.loads(m.group(0))

    def parse_jd(self, jd_text: str) -> dict:
        return self._json(PROMPT_JD_PARSE_V1 + jd_text)

    def generate_questions(self, requirements: dict, evidence: list[dict], max_questions: int = 5) -> list[dict]:
        raise NotImplementedError("wired in M2")

    def evaluate_answer(self, question: dict, answer: str, evidence: list[dict]) -> dict:
        raise NotImplementedError("wired in M3")

def get_adapter():
    if settings.llm_api_key:
        return GeminiRESTAdapter()
    return None
