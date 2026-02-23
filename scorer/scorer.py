# scorer/scorer.py
from sentence_transformers import SentenceTransformer, util
from scorer.resume_parser import extract_resume_text
from storage.models import Job
from config import MATCH_THRESHOLD
from loguru import logger

model = SentenceTransformer("all-MiniLM-L6-v2")

def score_jobs(jobs: list[Job]) -> list[Job]:
    resume_text = extract_resume_text()
    resume_emb  = model.encode(resume_text, convert_to_tensor=True)
    scored, passed = [], 0

    for job in jobs:
        # Skip scoring if description is too short to be meaningful
        if not job.description or len(job.description) < 50:
            job.match_score = 0.0
            logger.warning(f"  SKIP (no desc) — {job.title} @ {job.company}")
            scored.append(job)
            continue

        jd_emb          = model.encode(job.description, convert_to_tensor=True)
        similarity      = util.cos_sim(resume_emb, jd_emb).item()

        # cos_sim returns -1 to 1, normalize to 0-100
        job.match_score = round(((similarity + 1) / 2) * 100, 1)

        if job.match_score >= MATCH_THRESHOLD:
            passed += 1

        scored.append(job)
        logger.info(f"  {job.match_score}% — {job.title} @ {job.company}")

    logger.info(f"Scoring complete: {passed}/{len(scored)} above {MATCH_THRESHOLD}%")
    return sorted(scored, key=lambda j: j.match_score, reverse=True)