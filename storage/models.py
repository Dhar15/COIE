# storage/models.py
from dataclasses import dataclass, field

@dataclass
class Job:
    hash_id:            str
    title:              str
    company:            str
    location:           str
    source:             str
    url:                str
    description:        str  = ""
    posted_text:        str  = ""
    scraped_at:         str  = ""
    match_score:        float = 0.0
    recruiter:          str  = ""
    recruiter_title:    str  = ""
    recruiter_email:    str  = ""
    recruiter_linkedin: str  = ""
    email_subject:      str  = ""
    email_body:         str  = ""
    status:             str  = "New"