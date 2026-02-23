# COIE — Career Outreach Intelligence Engine

> A personal job search automation system that scrapes, scores, and surfaces the best roles for you — then helps you reach out to the right recruiter.

![Pipeline Overview](screenshots/Pipeline%20Overview.png)
![Job Feed](screenshots/Job%20Feed.png)
![Outreach Engine](screenshots/Outreach%20Queue.png)

---

## What It Does

COIE runs automatically twice a day and:

1. **Scrapes** LinkedIn and Naukri for desired roles at desired locations
2. **Scores** each job against your resume using semantic AI (sentence-transformers)
3. **Surfaces** high-match jobs in a live dashboard with filters and status tracking
4. **Emails** you a digest with direct apply links — readable on your phone
5. **Discovers** recruiter contacts via Hunter.io when you decide to pursue a role
6. **Drafts** a personalized 4–6 line outreach email via Groq (Llama 3.1) — opens pre-filled in Gmail

---

## Architecture

```
Windows Task Scheduler (9am + 6pm)
        ↓
scheduler/runner.py          ← orchestrates the pipeline
    ├── scraper/              ← Playwright scrapers (LinkedIn + Naukri)
    ├── scorer/               ← sentence-transformer scoring
    ├── storage/              ← SQLite database
    └── scheduler/notify.py  ← Gmail HTML digest

FastAPI (uvicorn, always-on)
    └── api/main.py           ← REST API + serves React dashboard

React Dashboard (COIE-dashboard/)
    └── src/App.jsx           ← Pipeline view, Job Feed, Outreach Queue

On-demand (user-triggered)
    ├── recruiter/hunter.py   ← Hunter.io recruiter discovery
    └── outreach/generator.py ← Groq email generation
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Scraping | Playwright (Python) |
| Scoring | sentence-transformers (all-MiniLM-L6-v2) |
| Backend | FastAPI + uvicorn |
| Database | SQLite |
| Frontend | React + Vite |
| Email Generation | Groq API (Llama 3.1 8B) — free |
| Recruiter Search | Hunter.io — free tier |
| Notifications | Python smtplib + Gmail |
| Scheduling | Windows Task Scheduler |
| Logging | Loguru (7-day rotation) |

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/yourusername/COIE.git
cd COIE
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Add your resume

```bash
# Place your resume at:
scorer/resume.pdf
```

### 4. Run the pipeline

```bash
python -m scheduler.runner
```

### 5. Start the API server

```bash
uvicorn api.main:app --port 8000
```

### 6. Build and open the dashboard

```bash
cd dashboard
npm install
npm run build
# Then open http://localhost:8000
```

---

## Configuration

Edit `config.py` to customize:

```python
KEYWORDS = [
    "Product Manager",
    "Associate Product Manager",
    YOUR_DESIRED_ROLES,
]

LOCATIONS = [
    "Bengaluru",
    "Hyderabad",
    YOUR_DESIRED_LOCATIONS,
]

MATCH_THRESHOLD    = 75   # shown in dashboard + email
OUTREACH_THRESHOLD = 75   # outreach queue + Hunter API
```

---

## Dashboard

| View | Description |
|------|-------------|
| Pipeline Overview | Stats, conversion funnel, top matches by source |
| Job Feed | All scored jobs with filters (score, source, location, recency) |
| Outreach Queue | 75%+ jobs — recruiter finder + email draft on demand |

---

## API Keys Required

| Service | Use | Cost |
|---------|-----|------|
| [Hunter.io](https://hunter.io) | Recruiter email discovery | Free (25/month) |
| [Groq](https://console.groq.com) | Email generation (Llama 3.1) | Free |
| Gmail App Password | Email notifications | Free |

---

## Project Structure

```
COIE/
├── api/
│   └── main.py             ← FastAPI endpoints
├── dashboard/
│   ├── src/
        ├── assets/
            ├── App.jsx     ← The front end dashboard
│   ├── dist                ← created by npm build
├── scraper/
│   ├── base_scraper.py
│   ├── linkedin_scraper.py
│   ├── naukri_scraper.py
│   └── deduplicator.py
├── scorer/
│   ├── resume_parser.py
│   └── scorer.py
├── recruiter/
│   └── hunter.py
├── outreach/
│   └── generator.py
├── scheduler/
│   ├── runner.py
│   └── notify.py
├── storage/
│   ├── models.py
│   └── database.py
├── data/                    ← created automatically
├── logs/                    ← created automatically
├── config.py
├── .env.example
└── requirements.txt
```

---

## Scheduling (Windows)

COIE uses Windows Task Scheduler for automation:

- **Pipeline**: runs `python -m scheduler.runner` at 09:00 and 18:00 daily
- **API server**: runs `uvicorn api.main:app --port 8000` at system startup

See the PRD for detailed Task Scheduler configuration.

---
