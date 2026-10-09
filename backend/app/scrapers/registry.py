from app.scrapers.base import BaseScraper
from app.scrapers.demo_directory import DemoDirectoryScraper
from app.scrapers.gmaps_playwright import GMapsPlaywrightScraper
from app.scrapers.google_places import GooglePlacesScraper

SCRAPERS: dict[str, BaseScraper] = {
    DemoDirectoryScraper.source_name: DemoDirectoryScraper(),
    GMapsPlaywrightScraper.source_name: GMapsPlaywrightScraper(),
    GooglePlacesScraper.source_name: GooglePlacesScraper(),
}


def get_scraper(source_name: str) -> BaseScraper:
    try:
        return SCRAPERS[source_name]
    except KeyError as exc:
        available = ", ".join(sorted(SCRAPERS))
        raise ValueError(f"Unsupported scraper source '{source_name}'. Available: {available}") from exc


def list_sources() -> list[str]:
    return sorted(SCRAPERS)
