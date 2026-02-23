# storage/database.py
import sqlite3, os
from storage.models import Job
from config import DB_PATH

def get_conn():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            hash_id      TEXT PRIMARY KEY,
            title        TEXT,
            company      TEXT,
            location     TEXT,
            source       TEXT,
            url          TEXT,
            description  TEXT,
            posted_text  TEXT,
            scraped_at   TEXT,
            match_score  REAL DEFAULT 0,
            recruiter    TEXT DEFAULT '',
            recruiter_title   TEXT DEFAULT '',
            recruiter_email   TEXT DEFAULT '',
            recruiter_linkedin TEXT DEFAULT '',
            email_subject     TEXT DEFAULT '',
            email_body        TEXT DEFAULT '',
            status            TEXT DEFAULT 'New'
        )""")

        # Add new columns to existing DB if running on old schema
        for col, definition in [
            ("recruiter_title",    "TEXT DEFAULT ''"),
            ("recruiter_linkedin", "TEXT DEFAULT ''"),
            ("email_subject",      "TEXT DEFAULT ''"),
            ("email_body",         "TEXT DEFAULT ''"),
        ]:
            try:
                conn.execute(f"ALTER TABLE jobs ADD COLUMN {col} {definition}")
            except Exception:
                pass  # Column already exists

def insert_job(job):
    with get_conn() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO jobs (
                hash_id, title, company, location, source,
                url, description, posted_text, scraped_at,
                match_score, recruiter, recruiter_title,
                recruiter_email, recruiter_linkedin,
                email_subject, email_body, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.hash_id,
            job.title,
            job.company,
            job.location,
            job.source,
            job.url,
            job.description,
            job.posted_text,
            job.scraped_at,
            job.match_score,
            "",   # recruiter
            "",   # recruiter_title
            "",   # recruiter_email
            "",   # recruiter_linkedin
            "",   # email_subject
            "",   # email_body
            "New" # status
        ))

def update_score(hash_id: str, score: float):
    with get_conn() as conn:
        conn.execute(
            "UPDATE jobs SET match_score=? WHERE hash_id=?",
            (score, hash_id))

def get_all_jobs() -> list:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT hash_id, title, company, location, source,
                   url, description, posted_text, scraped_at,
                   match_score, recruiter, recruiter_title,
                   recruiter_email, recruiter_linkedin,
                   email_subject, email_body, status
            FROM jobs
        """).fetchall()
    return [Job(**dict(r)) for r in rows]

def update_outreach(hash_id: str, recruiter: dict, email: dict):
    with get_conn() as conn:
        conn.execute("""
            UPDATE jobs SET
                recruiter          = ?,
                recruiter_title    = ?,
                recruiter_email    = ?,
                recruiter_linkedin = ?,
                email_subject      = ?,
                email_body         = ?
            WHERE hash_id = ?
        """, (
            recruiter.get("name", ""),
            recruiter.get("title", ""),
            recruiter.get("email", ""),
            recruiter.get("linkedin", ""),
            email.get("subject", ""),
            email.get("body", ""),
            hash_id
        ))