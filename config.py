# config.py
from dotenv import load_dotenv
import os

load_dotenv()

FRESHNESS_HOURS = 24
RESUME_PATH     = os.getenv("RESUME_PATH", "scorer/resume.pdf")
DB_PATH         = os.getenv("DB_PATH", "data/coie.db")
RUN_TIME1       = os.getenv("RUN_TIME", "09:00")
RUN_TIME2       = os.getenv("RUN_TIME2", "18:00")