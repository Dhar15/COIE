# scraper/naukri_scraper.py
import time
import random
from playwright.sync_api import Page
from scraper.base_scraper import BaseScraper
from storage.models import Job
from loguru import logger

STALE_SIGNALS = [
    "2 weeks", "3 weeks", "4 weeks", "1 month",
    "2 months", "3 months", "30 days",
]

class NaukriScraper(BaseScraper):
    SOURCE = "Naukri"

    def scrape(self, keywords, locations):
        from playwright.sync_api import sync_playwright
        jobs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,          # ← Run visible to bypass bot detection
                args=["--no-sandbox", "--start-maximized"]
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
                # Spoof WebGL and canvas fingerprint
                extra_http_headers={
                    "Accept-Language": "en-IN,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }
            )

            # Mask automation signals
            ctx.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en']});
            """)

            page = ctx.new_page()
            page.route(
                "**/*.{png,jpg,jpeg,gif,svg,webp,woff,woff2,ttf,mp4}",
                lambda r: r.abort()
            )

            seen = set()
            for kw in keywords:
                for loc in locations:
                    key = f"{kw.lower()}|{loc.lower()}"
                    if key in seen:
                        continue
                    seen.add(key)
                    try:
                        logger.info(f"[Naukri] Scraping: {kw} @ {loc}")
                        results = self._scrape_one(page, kw, loc)
                        jobs.extend(results)
                        logger.info(f"[Naukri] {kw} @ {loc} → {len(results)} jobs")
                    except Exception as e:
                        logger.error(f"[Naukri] Failed {kw}/{loc}: {e}")

                    # Random delay between requests — looks more human
                    time.sleep(random.uniform(2, 4))

            browser.close()

        fresh_jobs = []
        for job in jobs:
            posted = (job.posted_text or "").lower()
            # Keep if posted text is empty (unknown), recent, or not stale
            if not posted or not any(sig in posted for sig in STALE_SIGNALS):
                fresh_jobs.append(job)
            else:
                logger.warning(f"[Naukri] Skipping stale job ({job.posted_text}): {job.title} @ {job.company}")    
        
        return jobs

    def _scrape_one(self, page: Page, keyword: str, location: str) -> list[Job]:
        kw_slug  = keyword.lower().replace(' ', '-')
        loc_slug = location.lower().replace(' ', '-')
        url      = f"https://www.naukri.com/{kw_slug}-jobs-in-{loc_slug}?jobAge=7"

        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Check for access denied
        if "Access Denied" in page.title():
            logger.warning(f"[Naukri] Access denied for {url} — skipping")
            return []

        time.sleep(random.uniform(2, 3))

        # Dismiss popup
        try:
            page.keyboard.press("Escape")
            time.sleep(0.5)
        except:
            pass

        raw_cards = page.evaluate("""
            () => {
                const cards = document.querySelectorAll('div.cust-job-tuple');
                return Array.from(cards).slice(0, 15).map(card => {
                    const titleEl   = card.querySelector('.row1 h2 a.title');
                    const companyEl = card.querySelector('.row2 a.comp-name');
                    const locEl     = card.querySelector('.row3 .locWdth');
                    const expEl     = card.querySelector('.row3 .expwdth');
                    const descEl    = card.querySelector('.row4 .job-desc');
                    const postedEl  = card.querySelector('.row6 .job-post-day');
                    const tags      = Array.from(
                        card.querySelectorAll('.row5 .tag-li')
                    ).map(t => t.innerText.trim()).join(', ');
                    const descText  = descEl ? descEl.innerText.trim() : '';
                    return {
                        title:   titleEl   ? titleEl.innerText.trim()   : '',
                        url:     titleEl   ? titleEl.href               : '',
                        company: companyEl ? companyEl.innerText.trim() : '',
                        loc:     locEl     ? locEl.innerText.trim()     : '',
                        exp:     expEl     ? expEl.innerText.trim()     : '',
                        desc:    descText + (tags ? ' Skills: ' + tags  : ''),
                        posted:  postedEl  ? postedEl.innerText.trim()  : '',
                    };
                });
            }
        """)

        jobs = []
        for card in raw_cards:
            if not card["title"] or not card["company"]:
                continue
            jobs.append(self.make_job(
                title       = card["title"],
                company     = card["company"],
                location    = card["loc"] or location,
                url         = card["url"],
                description = card["desc"],
                posted_text = card["posted"],
            ))
        return jobs