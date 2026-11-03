from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://rightfit:rightfit_dev@localhost:5432/rightfit"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12
    invitation_ttl_hours: int = 168  # single-use assessment links, 7 days
    max_questions_per_round: int = 5  # locked rule: hard cap, recruiter-added included
    # LLM provider: Gemini-compatible REST by default; key arrives via env, never in the repo
    llm_api_key: str = ""
    llm_model: str = "gemini-2.0-flash"
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta"

settings = Settings()
