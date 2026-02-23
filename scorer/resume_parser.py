# scorer/resume_parser.py
import pdfplumber
from config import RESUME_PATH
from loguru import logger

def extract_resume_text() -> str:
    try:
        with pdfplumber.open(RESUME_PATH) as pdf:
            text = "\n".join(
                page.extract_text() or "" for page in pdf.pages
            )
        logger.info(f"Resume loaded: {len(text)} chars")
        return text.strip()
    except FileNotFoundError:
        logger.error(f"Resume not found at {RESUME_PATH}")
        raise