# test_cleanup.py
# Run from COIE root: python test_cleanup.py
import sqlite3
from datetime import datetime, timedelta
from storage.database import cleanup_old_jobs, get_conn

def insert_test_job(title, status, days_old):
    """Insert a fake job with a backdated scraped_at timestamp."""
    scraped_at = (datetime.now() - timedelta(days=days_old)).isoformat()
    with get_conn() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO jobs (hash_id, title, company, location, url, source, status, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"test_{title.replace(' ', '_')}",
            title, "Test Co", "Bengaluru",
            f"https://test.com/{title.replace(' ', '-')}",
            "Test", status, scraped_at
        ))

def count_test_jobs():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT title, status, scraped_at FROM jobs WHERE company = 'Test Co' ORDER BY scraped_at"
        ).fetchall()
    return rows

print("=== Inserting test jobs ===")
insert_test_job("New Job 3 days old",       "New",          3)
insert_test_job("New Job 8 days old",       "New",          8)
insert_test_job("New Job 10 days old",      "New",         10)
insert_test_job("Skipped Job 8 days old",   "Skipped",      8)
insert_test_job("Outreach Job 8 days old",  "Outreach Sent", 8)
insert_test_job("Replied Job 10 days old",  "Replied",     10)

print(f"Inserted 6 test jobs. Jobs before cleanup:")
for row in count_test_jobs():
    print(f"  [{row['status']:15}] {row['title']} (scraped: {row['scraped_at'][:10]})")

print("\n=== Running cleanup_old_jobs(days=7) ===")
cleanup_old_jobs(days=7)

remaining = count_test_jobs()
print(f"\nJobs after cleanup ({len(remaining)} remaining):")
for row in remaining:
    print(f"  [{row['status']:15}] {row['title']}")

print("\n=== Expected results ===")
print("  DELETED : New Job 8 days old       (New, > 7 days)")
print("  DELETED : New Job 10 days old      (New, > 7 days)")
print("  DELETED : Skipped Job 8 days old   (Skipped, > 7 days)")
print("  KEPT    : New Job 3 days old       (New, <= 7 days)")
print("  KEPT    : Outreach Job 8 days old  (Outreach Sent — always preserved)")
print("  KEPT    : Replied Job 10 days old  (Replied — always preserved)")

# Cleanup test data
print("\n=== Removing test data ===")
with get_conn() as conn:
    conn.execute("DELETE FROM jobs WHERE company = 'Test Co'")
print("Test data removed. DB is clean.")