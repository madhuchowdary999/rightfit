"use client";

import { useState } from "react";
import { api } from "../lib/api";

type Job = {
  id: string; title: string; jd_text: string; jd_version: number;
  requirements_json: { must_have: string[]; nice_to_have: string[]; seniority: string | null; domain: string | null } | null;
};

const TOKEN_KEY = "rightfit_token";

export default function RecruiterPage() {
  const [token, setToken] = useState<string | null>(() => {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(TOKEN_KEY);
  });
  const [mode, setMode] = useState<"login" | "signup">("signup");
  const [orgName, setOrgName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [title, setTitle] = useState("");
  const [jd, setJd] = useState("");
  const [job, setJob] = useState<Job | null>(null);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [candEmail, setCandEmail] = useState("");
  const [inviteLink, setInviteLink] = useState<string | null>(null);
  const [emailStatus, setEmailStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const run = async (fn: () => Promise<void>) => {
    setBusy(true); setErr(null);
    try { await fn(); } catch (e: any) { setErr(e.message || "something failed"); }
    finally { setBusy(false); }
  };

  const authBox = (
    <div className="card">
      <h2>{mode === "signup" ? "Sign up your agency" : "Sign in"}</h2>
      {mode === "signup" && (<><label>Agency name</label>
        <input value={orgName} onChange={(e) => setOrgName(e.target.value)} placeholder="Pilot Staffing Co" /></>)}
      <label>Your email</label>
      <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@agency.com" />
      <label>Password</label>
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button disabled={busy || !email || !password || (mode === "signup" && !orgName)}
        onClick={() => run(async () => {
          if (mode === "signup") {
            const r = await api.signup(orgName, email, password);
            const l = await api.login(email, password);
            window.localStorage.setItem(TOKEN_KEY, l.access_token);
            setToken(l.access_token);
          } else {
            const l = await api.login(email, password);
            window.localStorage.setItem(TOKEN_KEY, l.access_token);
            setToken(l.access_token);
          }
        })}>{mode === "signup" ? "Create account" : "Sign in"}</button>
      <p className="muted" style={{ marginTop: 8 }}>
        {mode === "signup" ? "Already registered? " : "New here? "}
        <a href="#" onClick={(e) => { e.preventDefault(); setMode(mode === "signup" ? "login" : "signup"); setErr(null); }}>
          {mode === "signup" ? "Sign in instead" : "Sign up"}
        </a>
      </p>
    </div>
  );

  return (
    <div className="wrap">
      <h1>RightFit · Recruiter portal</h1>
      <p className="muted">V1 MVP console. Create a job, review and correct the parsed requirements, invite a candidate.</p>

      {!token && authBox}
      {err && <div className="card"><p className="bad">{err}</p></div>}

      {token && (
        <>
          <p className="muted">Signed in. <a href="#" onClick={(e) => { e.preventDefault(); window.localStorage.removeItem(TOKEN_KEY); setToken(null); setJob(null); }}>Sign out</a></p>

          <div className="card">
            <h2>Create a job</h2>
            <label>Job title</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Senior Data Engineer" />
            <label>Job description</label>
            <textarea value={jd} onChange={(e) => setJd(e.target.value)} placeholder="Paste the JD here…" />
            <button disabled={busy || !title || !jd}
              onClick={() => run(async () => { setJob(await api.createJob(token, title, jd)); setInviteLink(null); setEditing(false); })}>
              Parse JD and create
            </button>
          </div>

          {job && (
            <div className="card">
              <h2>{job.title} <span className="muted">· JD v{job.jd_version}</span></h2>
              <p className="muted">Parsed requirements draft — correct anything the parser got wrong before inviting.</p>
              <div className="chips">
                {job.requirements_json?.must_have?.map((s) => <span key={s} className="chip">must: {s}</span>)}
                {job.requirements_json?.nice_to_have?.map((s) => <span key={s} className="chip">nice: {s}</span>)}
                {job.requirements_json?.seniority && <span className="chip">seniority: {job.requirements_json.seniority}</span>}
                {job.requirements_json?.domain && <span className="chip">domain: {job.requirements_json.domain}</span>}
              </div>

              {editing ? (
                <>
                  <label>Job description (editing creates JD v{job.jd_version + 1}; existing assessments keep their version)</label>
                  <textarea value={draft} onChange={(e) => setDraft(e.target.value)} />
                  <button disabled={busy || !draft}
                    onClick={() => run(async () => {
                      setJob(await api.updateJd(token, job.id, draft));
                      setEditing(false);
                    })}>Save new JD version</button>
                  <button style={{ background: "#64748b" }} onClick={() => setEditing(false)}>Cancel</button>
                </>
              ) : (
                <button style={{ background: "#64748b" }} onClick={() => { setDraft(job.jd_text); setEditing(true); }}>Edit JD</button>
              )}

              <label>Candidate email</label>
              <input value={candEmail} onChange={(e) => setCandEmail(e.target.value)} placeholder="candidate@example.com" />
              <button disabled={busy || !candEmail}
                onClick={() => run(async () => {
                  const r = await api.invite(token, job.id, candEmail);
                  setInviteLink(r.link);
                  setEmailStatus(r.email_status);
                })}>Send assessment invite</button>
              {inviteLink && (
                <p style={{ marginTop: 12 }}>
                  Single-use assessment link (valid 7 days): <a href={inviteLink}>{inviteLink}</a>
                  <br />
                  <span className="muted">Email delivery status: {emailStatus}</span>
                </p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
