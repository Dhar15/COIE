# scraper/base_scraper.py
import hashlib
from abc import ABC, abstractmethod
from storage.models import Job
from loguru import logger
from datetime import datetime

class BaseScraper(ABC):
    SOURCE = ""

    def scrape(self, keywords: list[str], locations: list[str]) -> list[Job]:
        """
        Default implementation for scrapers that don't need dual-page logic.
        LinkedIn overrides this entirely.
        """
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
            page = ctx.new_page()
            page.route(
                "**/*.{png,jpg,jpeg,gif,svg,webp,woff,woff2,ttf}",
                lambda r: r.abort()
            )

            for kw in keywords:
                for loc in locations:
                    try:
                        logger.info(f"[{self.SOURCE}] Scraping: {kw} @ {loc}")
                        results = self._scrape_one(page, kw, loc)
                        jobs.extend(results)
                        logger.info(
                            f"[{self.SOURCE}] {kw} @ {loc} → {len(results)} jobs"
                        )
                    except Exception as e:
                        logger.error(
                            f"[{self.SOURCE}] Failed {kw}/{loc}: {e}"
                        )
            browser.close()
        return jobs

    def _scrape_one(self, page, keyword: str, location: str) -> list[Job]:
        raise NotImplementedError

    def make_hash(self, title: str, company: str) -> str:
        raw = f"{title.lower().strip()}{company.lower().strip()}{self.SOURCE}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def make_job(self, title, company, location, url, description="", posted_text="") -> Job:
        # Generate hash from url (unique identifier)
        hash_id = hashlib.sha256(url.encode()).hexdigest()[:16]

        return Job(
            hash_id     = hash_id,
            title       = title,
            company     = company,
            location    = location,
            source      = self.SOURCE,
            url         = url,
            description = description,
            posted_text = posted_text,
            scraped_at  = datetime.now().isoformat(),
        )