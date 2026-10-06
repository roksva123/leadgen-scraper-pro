from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ScrapedLead:
    business_name: str
    phone_number: str | None = None
    address: str | None = None
    rating: float | None = None
    reviews_count: int | None = None
    website: str | None = None
    extra_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ScraperRequest:
    keyword: str
    location: str | None = None
    max_results: int = 25


class BaseScraper(ABC):
    source_name: str

    @abstractmethod
    async def scrape(self, request: ScraperRequest) -> list[ScrapedLead]:
        """Return normalized leads for the request."""
