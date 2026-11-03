"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "../../../lib/api";

type Question = { idx: number; skill: string; kind: string; text: string };

export default function AssessPage() {
  const token = (useParams().token as string) || "";
  const [state, setState] = useState<"loading" | "ready" | "done" | "error">("loading");
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [refs, setRefs] = useState<Record<number, string>>({});
  const [result, setResult] = useState<{ compatibility_score: number; gaps: string[] } | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api.startAssessment(token)
      .then((r: any) => {
        setAssessmentId(r.assessment_id);
        setQuestions(r.questions);
        setState("ready");
      })
      .catch((e: any) => { setErr(e.message); setState("error"); });
  }, [token]);

  const submit = async () => {
    if (!assessmentId) return;
    try {
      for (const q of questions) {
        const text = answers[q.idx] || "";
        const evRefs = (refs[q.idx] || "").split(",").map((s) => s.trim()).filter(Boolean);
        if (text.trim()) await api.answer(assessmentId, q.idx, text, evRefs);
      }
      setResult(await api.submitAssessment(assessmentId));
      setState("done");
    } catch (e: any) { setErr(e.message || "submission failed"); setState("error"); }
  };

  return (
    <div className="wrap">
      <h1>RightFit · Skill verification</h1>
      {state === "loading" && <p className="muted">Loading your assessment…</p>}
      {state === "error" && <div className="card"><p className="bad">{err || "This link is invalid or expired."}</p></div>}

      {state === "ready" && (
        <div className="card">
          <p className="muted">Answer the questions for this specific job. Attach evidence where you have it (certification ids, project names, references). You can leave a question empty.</p>
          {questions.map((q) => (
            <div className="q" key={q.idx}>
              <h2>{q.idx + 1}. {q.text}</h2>
              <textarea value={answers[q.idx] || ""} onChange={(e) => setAnswers({ ...answers, [q.idx]: e.target.value })} placeholder="Describe the specific task…" />
              <label>Evidence references (comma separated, optional)</label>
              <input value={refs[q.idx] || ""} onChange={(e) => setRefs({ ...refs, [q.idx]: e.target.value })} placeholder="cert:snowpro-core, task:claims-elt-2025" />
            </div>
          ))}
          <button disabled={!assessmentId} onClick={submit}>Submit assessment</button>
        </div>
      )}

      {state === "done" && result && (
        <div className="card">
          <h2>Submitted</h2>
          <p className="muted">Your verification report is ready for the recruiter. Score reflects this job's specific requirements and your evidence only.</p>
          <div className="score">{result.compatibility_score}%</div>
          {result.gaps.length > 0 && <p className="muted">Gaps flagged: {result.gaps.join(", ")}</p>}
        </div>
      )}
    </div>
  );
}
