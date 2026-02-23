# scraper/linkedin_scraper.py
import time
from playwright.sync_api import Page
from scraper.base_scraper import BaseScraper
from storage.models import Job
from loguru import logger

# Geographic IDs (confirmed correct)
GEO_IDS = {
    "Bengaluru": "105307040",
    "Bangalore":  "105307040",
    "Hyderabad":  "102639115",
    "Mumbai":     "103977742",
    "Remote":     "102713980",  # India-wide for remote
}

BLOCKED_SIGNALS = [
    # US
    "united states", "new york", "san francisco", "seattle",
    "austin", "chicago", "boston", "los angeles", "lensa",
    ", ca", ", wa", ", ny", ", tx",
    # Ireland
    "ireland", "dublin", "cork", "galway",
    # Other common false positives
    "united kingdom", "london", "singapore", "canada", "toronto",
    "australia", "sydney", "melbourne",
]

class LinkedInScraper(BaseScraper):
    SOURCE = "LinkedIn"

    def scrape(self, keywords, locations):
        from playwright.sync_api import sync_playwright
        jobs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800}
            )
            listing_page = ctx.new_page()
            listing_page.route(
                "**/*.{png,jpg,jpeg,gif,svg,webp,woff,woff2,ttf,mp4}",
                lambda r: r.abort()
            )

            seen_kw = set()
            for kw in keywords:
                for loc in locations:
                    key = f"{kw.lower()}|{loc.lower()}"
                    if key in seen_kw:
                        continue
                    seen_kw.add(key)
                    try:
                        logger.info(f"[LinkedIn] Scraping: {kw} @ {loc}")
                        results = self._scrape_one(listing_page, kw, loc)
                        jobs.extend(results)
                        logger.info(f"[LinkedIn] {kw} @ {loc} → {len(results)} jobs")
                    except Exception as e:
                        logger.error(f"[LinkedIn] Failed {kw}/{loc}: {e}")

            browser.close()
        return jobs

    def _scrape_one(self, listing_page: Page, keyword: str, location: str) -> list[Job]:

        geo_id = GEO_IDS.get(location, "102713980")  # fallback to India

        url = (
            "https://in.linkedin.com/jobs/search/"   # ← Indian subdomain
            f"?keywords={keyword.replace(' ', '%20')}"
            f"&location={location.replace(' ', '%20')}%2C%20India"
            f"&geoId={geo_id}"
            f"&f_TPR=r86400"
            f"&sortBy=DD"
        )

        listing_page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(2)

        # Scroll to trigger lazy-loaded cards
        for _ in range(3):
            listing_page.evaluate("window.scrollBy(0, 800)")
            time.sleep(0.8)

        # Wait for at least one card to appear, bail gracefully if none
        try:
            listing_page.wait_for_selector(
                "div.base-card", timeout=8000
            )
        except Exception:
            logger.warning(f"[LinkedIn] No cards found for {keyword} @ {location}")
            return []

        # Snapshot all card data BEFORE touching detail_page
        # We extract everything we need from the listing DOM in one pass
        raw_cards = listing_page.evaluate("""
            () => {
                const cards = document.querySelectorAll('div.base-card');
                return Array.from(cards).slice(0, 10).map(card => {
                    const titleEl   = card.querySelector('.base-search-card__title');
                    const companyEl = card.querySelector('.base-search-card__subtitle a');
                    const locEl     = card.querySelector('.job-search-card__location');
                    const timeEl    = card.querySelector('time');
                    const linkEl    = card.querySelector('a.base-card__full-link');
                    const snippetEl = card.querySelector('.base-search-card__metadata');

                    return {
                        title:   titleEl   ? titleEl.innerText.trim()                    : '',
                        company: companyEl ? companyEl.innerText.trim()                  : '',
                        loc:     locEl     ? locEl.innerText.trim()                      : '',
                        posted:  timeEl    ? timeEl.getAttribute('datetime')             : '',
                        url:     linkEl    ? linkEl.href                                 : '',
                        snippet: snippetEl ? snippetEl.innerText.trim()                  : '',
                    };
                });
            }
        """)

        jobs = []
        for card in raw_cards:
            if not card["title"] or not card["company"]:
                continue

            # Drop jobs with US location signals
            loc_check = (card["loc"] + card["url"]).lower()
            if any(sig in loc_check for sig in BLOCKED_SIGNALS):
                logger.warning(f"[LinkedIn] Skipping non-India job: {card['title']} @ {card['company']}")
                continue    

            jobs.append(self.make_job(
                title       = card["title"],
                company     = card["company"],
                location    = card["loc"] or location,
                url         = card["url"],
                description = card["snippet"],
                posted_text = card["posted"],
            ))

        return jobs