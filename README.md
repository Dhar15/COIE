# COIE — Career Outreach Intelligence Engine

> A personal job search automation system that scrapes, scores, and surfaces the best roles for you — then helps you reach out to the right recruiter.

![Pipeline Overview](screenshots/Pipeline%20Overview.png)
![Job Feed](screenshots/Job%20Feed.png)
![Outreach Engine](screenshots/Outreach%20Queue.png)

---

## What It Does

COIE runs automatically twice a day and:

1. **Scrapes** LinkedIn, Naukri, and Indeed for desired roles at desired locations
2. **Scores** each job against your resume using semantic AI (sentence-transformers) with experience and seniority penalties
3. **Surfaces** high-match jobs in a live dashboard with filters, status tracking, and Excel export
4. **Emails** you a digest with the top 10 matches and direct apply links — readable on your phone
5. **Discovers** recruiter contacts via Hunter.io (India-filtered) when you decide to pursue a role
6. **Drafts** a personalized 4–6 line outreach email via Groq (Llama 3.1) — opens pre-filled in Gmail

---

## Architecture

```
Windows Task Scheduler (9am + 6pm)
        ↓
scheduler/runner.py           ← orchestrates the pipeline
    ├── scraper/               ← Playwright scrapers (LinkedIn + Naukri + Indeed)
    ├── scorer/                ← sentence-transformer + experience/seniority penalties
    ├── storage/               ← SQLite database (auto-cleans stale jobs)
    └── scheduler/notify.py   ← Gmail HTML digest (top 10 matches)

FastAPI (uvicorn, always-on)
    └── api/main.py            ← REST API + serves React dashboard

React Dashboard (dashboard/)
    └── src/App.jsx            ← Pipeline, Job Feed, Outreach Queue, Settings

On-demand (user-triggered)
    ├── recruiter/hunter.py    ← Hunter.io recruiter discovery (India-filtered)
    └── outreach/generator.py ← Groq email generation
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Scraping | Playwright (Python) |
| Scoring | sentence-transformers (all-MiniLM-L6-v2) + rule-based penalties |
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

All user-facing settings are configurable from the **Settings panel** in the dashboard — no code changes needed. Settings are saved to `data/config.json` and take effect on the next pipeline run.

| Setting | Description | Default |
|---------|-------------|---------|
| Keywords | Job titles to search for | Product Manager, APM |
| Locations | Cities to search in | Bengaluru, Hyderabad |
| Match Threshold | Minimum score to show in Job Feed | 75% |
| Outreach Threshold | Minimum score for Outreach Queue | 75% |

Static configuration lives in `config.py`:

```python
RESUME_PATH     = "scorer/resume.pdf"
DB_PATH         = "data/coie.db"
RUN_TIME1       = "09:00"
RUN_TIME2       = "18:00"
FRESHNESS_HOURS = 24
```

Scorer configuration lives in `scorer/scorer.py`:

```python
CANDIDATE_YEARS = 3      # your total years of experience
CANDIDATE_LEVEL = "mid"  # "junior" | "mid" | "senior"
```

---

## Scoring System

COIE uses a hybrid scoring approach:

1. **Semantic similarity** — resume and JD are embedded using `all-MiniLM-L6-v2` and compared with cosine similarity
2. **Experience penalty** — jobs requiring significantly more years than you have are penalized (up to 45% reduction)
3. **Seniority penalty** — Senior/Lead/Director roles are penalized 20% for mid-level candidates

```
final_score = base_score × experience_multiplier × seniority_multiplier
```

This prevents 10+ year Senior roles from scoring identically to entry-level roles just because they share PM vocabulary.

---

## Dashboard

| View | Description |
|------|-------------|
| Pipeline Overview | Stats, conversion funnel, top 5 matches by source |
| Job Feed | Scored jobs with filters (score, source, location, recency) + Excel export |
| Outreach Queue | High-match jobs — recruiter finder + email draft on demand |
| Settings | Edit keywords, locations, and thresholds without touching code |

### Job Feed Features
- Filters: score threshold, source, location, posted date (Today / Last 3 days / This week)
- Skipped jobs accordion — review and un-skip jobs without losing them
- Unscored jobs accordion — jobs with no description (authwall or JS-rendered)
- One-click Excel export with color-coded match scores

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
│   └── main.py              ← FastAPI endpoints + config API + Excel export
├── dashboard/
│   ├── src/
│   │   └── App.jsx          ← React dashboard
│   └── dist/                ← created by npm run build
├── scraper/
│   ├── base_scraper.py
│   ├── linkedin_scraper.py
│   ├── naukri_scraper.py
│   ├── indeed_scraper.py
│   └── deduplicator.py      ← URL normalization + hash dedup
├── scorer/
│   ├── resume_parser.py
│   └── scorer.py            ← semantic + experience + seniority scoring
├── recruiter/
│   └── hunter.py            ← India-filtered recruiter discovery
├── outreach/
│   └── generator.py
├── scheduler/
│   ├── runner.py            ← pipeline orchestration + dynamic config
│   └── notify.py            ← HTML email digest (top 10 matches)
├── storage/
│   ├── models.py
│   └── database.py          ← auto-cleanup of stale jobs (7 days)
├── data/
│   ├── config.json          ← user settings (auto-created)
│   ├── coie.db              ← job database
│   └── seen_hashes.json     ← dedup memory (auto-resets every 7 days)
├── logs/                    ← created automatically
├── config.py                ← static config (paths, schedule times)
├── .env.example
└── requirements.txt
```

---

## Data Management

**`seen_hashes.json`** — prevents duplicate jobs across pipeline runs. Automatically resets every 7 days so fresh listings are always re-evaluated. If you change keywords or locations and want an immediate fresh scrape, delete this file manually.

**`coie.db`** — stores all jobs, scores, recruiter info, and outreach history. Never deleted automatically — your tracking data (Outreach Sent, Replied, Interview statuses) is preserved indefinitely. Jobs with `New` or `Skipped` status older than 7 days are cleaned up automatically.

To fully reset and start fresh:
```bash
del data\coie.db
del data\seen_hashes.json
```

---

## Scheduling (Windows)

COIE uses Windows Task Scheduler for automation:

- **Pipeline**: runs `python -m scheduler.runner` at 09:00 and 18:00 daily (configurable in `config.py`)
- **API server**: runs `uvicorn api.main:app --port 8000` at system logon with a 15-second delay

See the PRD for detailed Task Scheduler configuration.

---

## Known Limitations

- LinkedIn jobs often lack descriptions due to the authwall — these appear in the Unscored section and cannot be scored
- Indeed descriptions require the job panel to load after clicking — occasional misses land in Unscored
- Hunter.io free tier gives 25 recruiter searches/month — credits only consumed when you click "Perform Outreach"
- Config changes take effect on the next scheduled pipeline run, not immediately
- Adding a new location requires it to exist in the LinkedIn geoId map and Indeed location map — unknown locations fall back to India-wide search