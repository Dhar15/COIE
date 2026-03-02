# scheduler/runner.py
from apscheduler.schedulers.blocking import BlockingScheduler
from scheduler.notify import send_summary
from loguru import logger
import os
import json

from scraper.linkedin_scraper import LinkedInScraper
from scraper.naukri_scraper   import NaukriScraper
from scraper.deduplicator     import deduplicate
from scorer.scorer            import score_jobs
from storage.database         import init_db, insert_job, update_score, cleanup_old_jobs
from config                   import RUN_TIME1, RUN_TIME2

os.makedirs("logs", exist_ok=True)
logger.add("logs/coie.log", rotation="2 days", retention="7 days")

def load_config():
    path = "data/config.json"
    default = {
        "keywords":           ["Product Manager", "Associate Product Manager"],
        "locations":          ["Bengaluru", "Hyderabad"],
        "match_threshold":    75,
        "outreach_threshold": 75,
    }
    if os.path.exists(path):
        with open(path) as f:
            return {**default, **json.load(f)}
    return default

def run_pipeline():
    cfg                = load_config()        #Fresh read every run
    KEYWORDS           = cfg["keywords"]
    LOCATIONS          = cfg["locations"]
    MATCH_THRESHOLD    = cfg["match_threshold"]
    OUTREACH_THRESHOLD = cfg["outreach_threshold"]

    init_db()
    cleanup_old_jobs(days=7)

    logger.info("=" * 50)
    logger.info("COIE Pipeline Started")
    logger.info("=" * 50)

    # 1. Scrape
    all_jobs = []
    for Scraper in [LinkedInScraper, NaukriScraper]:
        jobs = Scraper().scrape(KEYWORDS, LOCATIONS)
        all_jobs.extend(jobs)
        logger.info(f"{Scraper.SOURCE}: {len(jobs)} jobs fetched")

    # 2. Deduplicate
    unique_jobs = deduplicate(all_jobs)
    logger.info(f"After dedup: {len(unique_jobs)} unique jobs")

    # 3. Store all unique jobs
    for job in unique_jobs:
        if not isinstance(job.title, str):
            logger.warning(f"Bad title type: {type(job.title)} — {job.title} @ {job.company}")
        insert_job(job)

    # 4. Score
    scored_jobs = score_jobs(unique_jobs, match_threshold=MATCH_THRESHOLD)

    # 5. Update scores in DB
    for job in scored_jobs:
        update_score(job.hash_id, job.match_score)

    # 6. Summary
    high = [j for j in scored_jobs if j.match_score >= MATCH_THRESHOLD]
    
    logger.info(f"Pipeline done. {len(high)} jobs above {MATCH_THRESHOLD}% threshold.")
    for j in high:
        logger.info(f"  ★ {j.match_score}% | {j.title} @ {j.company} [{j.source}]")

    logger.info("=" * 50)

    # Send email summary
    send_summary(
        total      = len(all_jobs),
        unique     = len(unique_jobs),
        high_match = len(high),
        threshold  = MATCH_THRESHOLD,
        top_jobs   = [
            {
                "title": j.title, 
                "company": j.company,
                "match_score": j.match_score, 
                "source": j.source,
                "url": j.url
            }
            for j in high
        ][:10]  # Top 10 jobs
    )


if __name__ == "__main__":
    # Run once immediately, then schedule
    run_pipeline()

    h, m = RUN_TIME1.split(":")
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, "cron", hour=int(h), minute=int(m))
    h, m = RUN_TIME2.split(":")
    scheduler.add_job(run_pipeline, "cron", hour=int(h), minute=int(m))
    logger.info(f"Scheduler armed: next run at {RUN_TIME1} and {RUN_TIME2} daily")
    scheduler.start()