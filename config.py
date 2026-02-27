# config.py
from dotenv import load_dotenv
import os

load_dotenv()

# Kept tight intentionally — 3 keywords × 2 locations = 6 requests max per scraper
# Expand once the scraper is stable
KEYWORDS = [
    "Product Manager",
    "Associate Product Manager",
]

LOCATIONS = [
    "Bengaluru",
    "Hyderabad",
]

FRESHNESS_HOURS = 24
MATCH_THRESHOLD = int(os.getenv("MATCH_THRESHOLD", 75))
OUTREACH_THRESHOLD = int(os.getenv("OUTREACH_THRESHOLD", 75))
RESUME_PATH     = os.getenv("RESUME_PATH", "scorer/resume.pdf")
DB_PATH         = os.getenv("DB_PATH", "data/coie.db")
RUN_TIME1       = os.getenv("RUN_TIME", "09:00")
RUN_TIME2       = os.getenv("RUN_TIME2", "18:00")