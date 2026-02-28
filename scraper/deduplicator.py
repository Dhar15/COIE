# scraper/deduplicator.py
import json, os, hashlib
from urllib.parse import urlparse
from storage.models import Job

HASH_FILE = "data/seen_hashes.json"

def load_seen() -> set:
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen: set):
    os.makedirs("data", exist_ok=True)
    with open(HASH_FILE, "w") as f:
        json.dump(list(seen), f)

def normalize_url(url: str) -> str:
    """Strip tracking params — keep only the base job URL."""
    if not url:
        return url
    parsed = urlparse(url)
    if "linkedin.com" in (parsed.netloc or ""):
        path = parsed.path.rstrip("/")
        return f"https://www.linkedin.com{path}"
    if "naukri.com" in (parsed.netloc or ""):
        return f"https://www.naukri.com{parsed.path}"
    return url

def deduplicate(jobs: list[Job]) -> list[Job]:
    seen   = load_seen()
    unique = []
    for job in jobs:
        clean     = normalize_url(job.url) or job.url
        norm_hash = hashlib.sha256(str(clean).encode()).hexdigest()[:16]
        if norm_hash not in seen:
            seen.add(norm_hash)
            job.url     = clean
            job.hash_id = norm_hash
            unique.append(job)
    save_seen(seen)
    return unique# scraper/deduplicator.py
import json, os, hashlib
from urllib.parse import urlparse
from storage.models import Job

HASH_FILE = "data/seen_hashes.json"

def load_seen() -> set:
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen: set):
    os.makedirs("data", exist_ok=True)
    with open(HASH_FILE, "w") as f:
        json.dump(list(seen), f)

def normalize_url(url: str) -> str:
    """Strip tracking params — keep only the base job URL."""
    if not url:
        return url
    parsed = urlparse(url)
    if "linkedin.com" in (parsed.netloc or ""):
        path = parsed.path.rstrip("/")
        return f"https://www.linkedin.com{path}"
    if "naukri.com" in (parsed.netloc or ""):
        return f"https://www.naukri.com{parsed.path}"
    return url

def deduplicate(jobs: list[Job]) -> list[Job]:
    seen   = load_seen()
    unique = []
    for job in jobs:
        clean     = normalize_url(job.url) or job.url
        norm_hash = hashlib.sha256(str(clean).encode()).hexdigest()[:16]
        if norm_hash not in seen:
            seen.add(norm_hash)
            job.url     = clean
            job.hash_id = norm_hash
            unique.append(job)
    save_seen(seen)
    return unique