from sentence_transformers import SentenceTransformer, util
from scorer.resume_parser import extract_resume_text
from storage.models import Job
from loguru import logger
import re

model = SentenceTransformer("all-MiniLM-L6-v2")

# ← Set this once to reflect your actual experience
CANDIDATE_YEARS = 3
CANDIDATE_LEVEL = "mid"   # "junior" | "mid" | "senior"

SENIOR_KEYWORDS = ["senior", "lead", "staff", "principal", "director", "head of", "vp ", "vice president", "group pm"]

WORD_TO_NUM = {
    "one":1, "two":2, "three":3, "four":4, "five":5,
    "six":6, "seven":7, "eight":8, "nine":9, "ten":10,
    "eleven":11, "twelve":12, "fifteen":15, "twenty":20
}

def extract_required_experience(text: str) -> int | None:
    t = text.lower()

    # Replace word numbers with digits first
    for word, num in WORD_TO_NUM.items():
        t = re.sub(rf'\b{word}\b', str(num), t)

    patterns = [
        # Ranges — always take lower bound
        r'(\d+)\s*(?:–|-|to)\s*\d+\s*(?:\+)?\s*(?:years?|yrs?)',            # "7-8 Yrs", "7–10 years"

        # Explicit minimums
        r'minimum\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)',                     # "minimum of 5 years"
        r'at\s*least\s*(\d+)\s*(?:years?|yrs?)',                            # "at least 8 years"

        # "N+ years of [ANYTHING UP TO 4 WORDS] experience"
        r'(\d+)\+?\s*(?:years?|yrs?)\s*of\s*(?:\w+\s*){0,4}experience',     # "12+ years of IT experience"

        # "N years [verb] in/as/at ..." — working, serving, leading etc.
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:working|serving|leading|managing|building|developing)',

        # "experience of N years"
        r'experience\s*of\s*(\d+)\s*(?:\+)?\s*(?:years?|yrs?)',

        # Standard "N years of experience" / "N years experience"
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:relevant\s*|work\s*|total\s*)?experience',

        # Last resort — any standalone "N+ years" or "N yrs"
        r'(\d+)\s*\+\s*(?:years?|yrs?)',                                    # "5+ yrs"
        r'\b(\d{1,2})\s*(?:years?|yrs?)\b',                                 # "15 years" anywhere
    ]

    for pat in patterns:
        m = re.search(pat, t)
        if m:
            return int(m.group(1))

    return None

def experience_penalty(required: int | None) -> float:
    if required is None: return 1.0
    gap = required - CANDIDATE_YEARS
    if gap <= 0:  return 1.0
    elif gap <= 2: return 0.90
    elif gap <= 5: return 0.75
    else:          return 0.55

def seniority_penalty(text: str, title: str = "") -> float:
    combined = (text + " " + title).lower() 
    if any(kw in combined for kw in SENIOR_KEYWORDS):
        return 0.80 if CANDIDATE_LEVEL != "senior" else 1.0

    return 1.0

def score_jobs(jobs: list[Job], match_threshold: float = 75) -> list[Job]:
    resume_text = extract_resume_text()
    resume_emb  = model.encode(resume_text, convert_to_tensor=True)
    scored, passed = [], 0

    for job in jobs:
        if not job.description or len(job.description) < 50:
            job.match_score = 0.0
            logger.warning(f"  SKIP (no desc) — {job.title} @ {job.company}")
            scored.append(job)
            continue

        jd_emb     = model.encode(job.description, convert_to_tensor=True)
        similarity = util.cos_sim(resume_emb, jd_emb).item()
        base_score = ((similarity + 1) / 2) * 100

        # Apply penalties
        required_exp = extract_required_experience(job.description)
        exp_mult     = experience_penalty(required_exp)
        sen_mult     = seniority_penalty(job.description, job.title)
        final_score  = round(base_score * exp_mult * sen_mult, 1)

        job.match_score = final_score

        if final_score >= match_threshold:
            passed += 1

        logger.info(
            f"  {final_score}% (base:{round(base_score,1)}% "
            f"exp_req:{required_exp}yr exp_mult:{exp_mult} sen_mult:{sen_mult}) "
            f"— {job.title} @ {job.company}"
        )

        scored.append(job)

    logger.info(f"Scoring complete: {passed}/{len(scored)} above {match_threshold}%")
    return sorted(scored, key=lambda j: j.match_score, reverse=True)
