const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function req(path: string, init?: RequestInit, token?: string | null) {
  const res = await fetch(API + path, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...init,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  signup: (org_name: string, email: string, password: string) =>
    req("/auth/signup", { method: "POST", body: JSON.stringify({ org_name, email, password }) }),
  login: (email: string, password: string) =>
    req("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  createJob: (token: string, title: string, jd_text: string) =>
    req("/jobs", { method: "POST", body: JSON.stringify({ title, jd_text }) }, token),
  updateJd: (token: string, job_id: string, jd_text: string) =>
    req(`/jobs/${job_id}/jd?jd_text=${encodeURIComponent(jd_text)}`, { method: "PUT" }, token),
  getJob: (token: string, job_id: string) => req(`/jobs/${job_id}`, undefined, token),
  invite: (token: string, job_id: string, candidate_email: string) =>
    req("/invitations", { method: "POST", body: JSON.stringify({ job_id, candidate_email }) }, token),
  startAssessment: (token: string) => req(`/assessments/start/${token}`),
  answer: (assessment_id: string, question_idx: number, response: string, evidence_refs: string[]) =>
    req(`/assessments/${assessment_id}/answer`, { method: "POST", body: JSON.stringify({ question_idx, response, evidence_refs }) }),
  submitAssessment: (assessment_id: string) =>
    req(`/assessments/${assessment_id}/submit`, { method: "POST" }),
};
