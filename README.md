# RightFit
B2B SaaS: job-specific candidate skill verification for recruiters and staffing agencies.
Recruiter portal (jobs, JD parsing, assessments), candidate flow (email-verified, single-use link,
no account required), admin dashboard. Outputs: verification report, compatibility score,
skill gaps, CSV export. V1 has no automatic job applications. Revenue: B2B subscription.

Architecture decisions (Nov 2 2026):
- Backend: Python 3.12 / FastAPI / SQLAlchemy 2 / PostgreSQL 16 / Alembic
- Frontend: Next.js 15 (App Router) + TypeScript + Tailwind
- AI: provider-agnostic LLM adapter (JD parsing, question generation, answer evaluation), prompts versioned in repo
- Rules locked in product reviews: max 5 verification questions per candidate per round (recruiter-added included);
  evidence-first verification (no Verified label without an evidence source); a completed task proves that task only;
  JD version changes never overwrite existing candidate cases; no mandatory AI interview.

Build order: M1 scaffold/auth/orgs/jobs/JD parse -> M2 invitations/candidate flow/assessment engine ->
M3 evaluation/report/CSV/admin -> M4 pilot with first agency.
