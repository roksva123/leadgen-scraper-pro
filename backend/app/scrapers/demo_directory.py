import hashlib
import random

from app.scrapers.base import BaseScraper, ScrapedLead, ScraperRequest
from app.scrapers.cleaner import dedupe_leads
from app.scrapers.rate_limit import random_delay


class DemoDirectoryScraper(BaseScraper):
    """Demo-safe scraper that generates realistic sample leads for development and demos."""

    source_name = "demo_directory"

    async def scrape(self, request: ScraperRequest) -> list[ScrapedLead]:
        await random_delay()
        seed = int(hashlib.sha256(f"{request.keyword}:{request.location}".encode()).hexdigest(), 16)
        rng = random.Random(seed)
        location = request.location or "Indonesia"
        categories = ["Cafe", "Restaurant", "Clinic", "Agency", "Studio", "Workshop"]

        leads: list[ScrapedLead] = []
        for index in range(request.max_results):
            category = rng.choice(categories)
            name = f"{request.keyword.title()} {category} {index + 1}"
            leads.append(
                ScrapedLead(
                    business_name=name,
                    phone_number=f"+62 812-{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}",
                    address=f"Jl. Contoh No. {rng.randint(1, 200)}, {location}",
                    rating=round(rng.uniform(3.7, 5.0), 1),
                    reviews_count=rng.randint(5, 900),
                    website=f"https://example.com/{name.lower().replace(' ', '-')}",
                    extra_metadata={"source": self.source_name, "demo": True},
                )
            )
        return dedupe_leads(leads)
