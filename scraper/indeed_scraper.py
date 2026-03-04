# scraper/indeed_scraper.py
import time
import random
import re
from playwright.sync_api import Page
from scraper.base_scraper import BaseScraper
from storage.models import Job
from loguru import logger

# Map city names to Indeed location strings
INDEED_LOCATIONS = {
    "Bengaluru":  "Bengaluru, Karnataka",
    "Bangalore":  "Bengaluru, Karnataka",
    "Hyderabad":  "Hyderabad, Telangana",
    "Mumbai":     "Mumbai, Maharashtra",
    "Delhi":      "Delhi, Delhi",
    "New Delhi":  "New Delhi, Delhi",
    "Pune":       "Pune, Maharashtra",
    "Chennai":    "Chennai, Tamil Nadu",
    "Kolkata":    "Kolkata, West Bengal",
    "Gurgaon":    "Gurugram, Haryana",
    "Gurugram":   "Gurugram, Haryana",
    "Noida":      "Noida, Uttar Pradesh",
    "Remote":     "Remote",
}

STALE_SIGNALS = ["30+ days ago", "1 month ago", "2 months ago"]

class IndeedScraper(BaseScraper):
    SOURCE = "Indeed"

    def scrape(self, keywords, locations):
        from playwright.sync_api import sync_playwright
        jobs = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled", "--start-maximized"]
            )
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1366, "height": 768},
                locale="en-IN",
                timezone_id="Asia/Kolkata",
                extra_http_headers={
                    "Accept-Language": "en-IN,en;q=0.9",
                }
            )
            ctx.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)

            page = ctx.new_page()

            seen_combos = set()
            for kw in keywords:
                for loc in locations:
                    key = f"{kw.lower()}|{loc.lower()}"
                    if key in seen_combos:
                        continue
                    seen_combos.add(key)

                    try:
                        logger.info(f"[Indeed] Scraping: {kw} @ {loc}")
                        results = self._scrape_one(page, kw, loc)
                        jobs.extend(results)
                        logger.info(f"[Indeed] {kw} @ {loc} → {len(results)} jobs")
                    except Exception as e:
                        logger.error(f"[Indeed] Failed {kw}/{loc}: {e}")

                    time.sleep(random.uniform(2, 4))

            browser.close()

        # Filter stale jobs
        fresh = []
        for job in jobs:
            posted = (job.posted_text or "").lower()
            if not posted or not any(s in posted for s in STALE_SIGNALS):
                fresh.append(job)
            else:
                logger.warning(f"[Indeed] Skipping stale ({job.posted_text}): {job.title} @ {job.company}")

        return fresh

    def _scrape_one(self, page: Page, keyword: str, location: str) -> list[Job]:
        indeed_loc = INDEED_LOCATIONS.get(location, location)
        q = keyword.replace(' ', '+')
        l = indeed_loc.replace(' ', '+').replace(',', '%2C')
        url = f"https://in.indeed.com/jobs?q={q}&l={l}&fromage=7&radius=25"

        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        if "sorry" in page.title().lower() or "blocked" in page.title().lower():
            logger.warning(f"[Indeed] Blocked — skipping")
            return []

        # Wait explicitly for job cards to render
        try:
            page.wait_for_selector(".resultContent", timeout=8000)
        except:
            logger.warning(f"[Indeed] .resultContent never appeared — page title: {page.title()}")
            return []    

        time.sleep(random.uniform(2, 3))
        try:
            page.keyboard.press("Escape")
        except:
            pass

        # Extract all job data in one JS call — find elements WITH data-jk
        raw_cards = page.evaluate("""
            () => {
                // data-jk is on the <a> inside <h2>, not on the card container
                const anchors = document.querySelectorAll('h2 a[data-jk]');
                const results = [];
                const seen = new Set();

                Array.from(anchors).slice(0, 15).forEach(a => {
                    const jk = a.getAttribute('data-jk');
                    if (!jk || seen.has(jk)) return;
                    seen.add(jk);

                    // Walk up to job_seen_beacon container
                    let container = a;
                    for (let i = 0; i < 8; i++) {
                        if (container?.classList?.contains('job_seen_beacon')) break;
                        container = container?.parentElement;
                    }

                    const title   = a.querySelector('span[title]')?.getAttribute('title')
                                || a.querySelector('span')?.innerText?.trim() || '';
                    const compEl  = container?.querySelector('[data-testid="company-name"]');
                    const locEl   = container?.querySelector('[data-testid="text-location"]');

                    const cardWrapper = container || a.closest('div.job_seen_beacon');
                    const dateEl = cardWrapper?.querySelector(
                        '.heading6.tapItem-gutter [class*="date"], ' +
                        '[class*="jobMetaData"] [class*="date"], ' +
                        'table [class*="date"], ' +
                        '.underShelfFooter [class*="date"]'
                    );

                    // Fallback — any element containing "ago" or "day" text near the card
                    const allSpans = cardWrapper ? Array.from(cardWrapper.querySelectorAll('span')) : [];
                    const dateSpan = allSpans.find(s => /(\\d+\s*(day|hour|minute)|just now|today)/i.test(s.innerText));
                    const posted = dateEl?.innerText?.trim() || dateSpan?.innerText?.trim() || '';

                    const company = compEl?.innerText?.trim() || '';
                    const loc     = locEl?.innerText?.trim() || '';

                    if (title && company) {
                        results.push({ jk, title, company, loc, posted });
                    }
                });

                return results;
            }
        """)

        if not raw_cards:
            return []

        jobs = []
        for card in raw_cards:
            jk           = card.get("jk", "")
            title_text   = card.get("title", "")
            company_text = card.get("company", "")

            if not jk or not title_text or not company_text:
                continue

            # Click the card to load JD in right panel
            try:
                el = page.query_selector(f'h2 a[data-jk="{jk}"]')
                if el:
                    try:
                        el.click(timeout=5000, force=True)  
                        time.sleep(1.5)                       
                    except Exception as e:
                        logger.warning(f"[Indeed] Click failed for {jk}: {e}")
                        desc = ""

                    desc = page.evaluate("""
                        () => {
                            const sels = [
                                '#jobDescriptionText',
                                '.jobsearch-jobDescriptionText',
                                '[id*="jobDescription"]',
                                '[class*="jobDescription"]',
                            ];
                            for (const s of sels) {
                                const el = document.querySelector(s);
                                if (el && el.innerText.trim().length > 100)
                                    return el.innerText.trim();
                            }
                            return '';
                        }
                    """)
                else:
                    desc = ""
            except Exception as e:
                logger.warning(f"[Indeed] Click failed for {jk}: {e}")
                desc = ""

            job_url = f"https://in.indeed.com/viewjob?jk={jk}"
            jobs.append(self.make_job(
                title       = title_text,
                company     = company_text,
                location    = card.get("loc") or location,
                url         = job_url,
                description = desc[:3000] if desc else "",
                posted_text = card.get("posted") or "Today",
            ))

        scored = sum(1 for j in jobs if j.description and len(j.description) > 50)
        logger.info(f"[Indeed] {len(jobs)} jobs, {scored} with JD — {keyword} @ {location}")    

        return jobs

    