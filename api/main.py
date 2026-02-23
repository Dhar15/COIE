# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import sys
from storage.database import init_db

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MATCH_THRESHOLD, OUTREACH_THRESHOLD, DB_PATH

app = FastAPI(title="COIE API")
@app.on_event("startup")
def startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/jobs")
def get_jobs(min_score: float = 0, limit: int = 100):
    """Return all jobs sorted by match score."""
    with get_conn() as conn:
       rows = conn.execute("""
            SELECT hash_id, title, company, location, source,
                   url, posted_text, scraped_at, match_score,
                   recruiter, recruiter_title, recruiter_email,
                   recruiter_linkedin, email_subject, email_body, status
            FROM jobs
            WHERE match_score >= ?
            ORDER BY match_score DESC
            LIMIT ?
        """, (min_score, limit)).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/stats")
def get_stats():
    """Return pipeline summary stats for the dashboard."""
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        high  = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE match_score >= ?",
            (MATCH_THRESHOLD,)
        ).fetchone()[0]
        # Count jobs that ever reached "Outreach Sent" or beyond
        sent = conn.execute("""
            SELECT COUNT(*) FROM jobs 
            WHERE status IN ('Outreach Sent', 'Replied', 'Interview')
        """).fetchone()[0]
        # Count jobs that ever reached "Replied" or beyond
        replied = conn.execute("""
            SELECT COUNT(*) FROM jobs 
            WHERE status IN ('Replied', 'Interview')
        """).fetchone()[0]
        by_source = conn.execute("""
            SELECT source, COUNT(*) as count
            FROM jobs GROUP BY source
        """).fetchall()
        top_jobs = conn.execute("""
            SELECT title, company, match_score, source, status
            FROM jobs
            WHERE match_score >= ?
            ORDER BY match_score DESC
            LIMIT 5
        """, (MATCH_THRESHOLD,)).fetchall()

    return {
        "total_scraped":        total,
        "high_match":           high,
        "outreach_sent":        sent,
        "replies":              replied,
        "threshold":            MATCH_THRESHOLD,
        "outreach_threshold":   OUTREACH_THRESHOLD,
        "reply_rate":           round((replied / sent * 100) if sent > 0 else 0, 1),
        "by_source":            [dict(r) for r in by_source],
        "top_jobs":             [dict(r) for r in top_jobs],
    }


@app.patch("/api/jobs/{hash_id}/status")
def update_status(hash_id: str, body: dict):
    """Update job status (e.g. Outreach Sent, Replied)."""
    status = body.get("status")
    if not status:
        return {"error": "status required"}
    with get_conn() as conn:
        conn.execute(
            "UPDATE jobs SET status = ? WHERE hash_id = ?",
            (status, hash_id)
        )
    return {"ok": True, "hash_id": hash_id, "status": status}


@app.patch("/api/jobs/{hash_id}/recruiter")
def update_recruiter(hash_id: str, body: dict):
    """Manually add recruiter name + email."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE jobs SET recruiter = ?, email = ? WHERE hash_id = ?",
            (body.get("recruiter", ""), body.get("email", ""), hash_id)
        )
    return {"ok": True}

@app.post("/api/jobs/{hash_id}/outreach")
def perform_outreach(hash_id: str):
    """Trigger Hunter + Groq for a specific job on demand."""
    from recruiter.hunter   import find_recruiter
    from outreach.generator import generate_email
    from storage.database   import update_outreach

    # Fetch the job from DB
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE hash_id = ?", (hash_id,)
        ).fetchone()

    if not row:
        return {"error": "Job not found"}

    job = dict(row)

    if not job.get("description") or len(job["description"]) < 50:
        return {"error": "No job description available to personalize email"}

    # Hunter recruiter lookup
    recruiter = find_recruiter(job["company"], job["location"]) or {}

    # Groq email generation
    email = generate_email(
        job_title       = job["title"],
        company         = job["company"],
        job_description = job["description"],
        recruiter       = recruiter,
    )

    if not email:
        return {"error": "Email generation failed"}

    update_outreach(hash_id, recruiter, email)

    return {
        "ok":               True,
        "recruiter":        recruiter.get("name", ""),
        "recruiter_email":  recruiter.get("email", ""),
        "email_subject":    email["subject"],
        "email_body":       email["body"],
    }

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="dashboard/dist", html=True), name="static")