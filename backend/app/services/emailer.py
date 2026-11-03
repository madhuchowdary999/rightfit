"""Invite email: real SMTP when env config exists, durable outbox rows otherwise."""
import os, smtplib, traceback
from email.message import EmailMessage
from ..models import EmailOutbox

def send_invite(db, to_email: str, org_name: str, job_title: str, link: str, expires_iso: str) -> str:
    subject = f"Skill verification invite: {job_title}"
    body = (f"Hello,\n\n{org_name} invited you to verify your skills for the role of {job_title}.\n\n"
            f"Your single-use assessment link (valid until {expires_iso[:10]}):\n{link}\n\n"
            f"RightFit — job-specific verification, five questions, your evidence.")
    host = os.getenv("SMTP_HOST")
    outbox = EmailOutbox(to_email=to_email, subject=subject, body=body)
    db.add(outbox)
    db.commit()
    if not host:
        outbox.status = "queued_no_smtp"
        return "queued_no_smtp"
    msg = EmailMessage()
    msg["From"] = os.getenv("SMTP_FROM", "no-reply@rightfit.local")
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            if os.getenv("SMTP_USER"):
                s.login(os.getenv("SMTP_USER", ""), os.getenv("SMTP_PASSWORD", ""))
            s.send_message(msg)
        outbox.status = "sent"
        return "sent"
    except Exception:
        outbox.status = "failed"
        outbox.error = traceback.format_exc()[-800:]
        return "failed"
