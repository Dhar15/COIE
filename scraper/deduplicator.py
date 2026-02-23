# scraper/deduplicator.py
import json, os
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

def deduplicate(jobs: list[Job]) -> list[Job]:
    seen   = load_seen()
    unique = []
    for job in jobs:
        if job.hash_id not in seen:
            seen.add(job.hash_id)
            unique.append(job)
    save_seen(seen)
    return unique