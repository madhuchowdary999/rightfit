from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import engine, Base
from . import models  # noqa: F401  (register tables)
from .routers import auth, jobs, invitations, assessments, reports

app = FastAPI(title="RightFit API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(invitations.router)
app.include_router(assessments.router)
app.include_router(reports.router)
