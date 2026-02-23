# recruiter/hunter.py
import requests
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
HUNTER_KEY = os.getenv("HUNTER_API_KEY")

def find_recruiter(company_name: str, location: str = None) -> dict | None:
    if not HUNTER_KEY:
        logger.error("HUNTER_API_KEY not set in .env")
        return None

    try:
        resp = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={
                "company":        company_name,   # Hunter resolves domain internally
                "department":     "hr",
                "seniority":      "senior,executive,junior",
                "required_field": "full_name,position",
                "type":           "personal",
                "limit":          10,
                "api_key":        HUNTER_KEY,
            },
            timeout=10
        )
        resp.raise_for_status()
        data   = resp.json().get("data", {})
        domain = data.get("domain", company_name)
        emails = data.get("emails", [])

        if not emails:
            logger.warning(f"[Hunter] No HR emails found for {company_name} ({domain})")
            return None

        # Prefer recruiter/talent titles
        recruiter_keywords = ["recruiter", "talent", "hiring", "hr", "people", "acquisition"]
        best = None
        for e in emails:
            title = (e.get("position") or "").lower()
            if any(kw in title for kw in recruiter_keywords):
                best = e
                break

        if not best:
            best = emails[0]

        name  = f"{best.get('first_name','')} {best.get('last_name','')}".strip()
        email = best.get("value", "")

        logger.info(f"[Hunter] Found: {name} <{email}> @ {domain}")
        return {
            "name":     name,
            "email":    email,
            "title":    best.get("position", ""),
            "linkedin": best.get("linkedin", ""),
        }

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"[Hunter] Company not found: {company_name}")
        elif e.response.status_code == 429:
            logger.warning("[Hunter] Rate limit hit")
        else:
            logger.error(f"[Hunter] HTTP error for {company_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"[Hunter] Error for {company_name}: {e}")
        return None