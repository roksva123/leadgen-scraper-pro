from urllib.parse import urlencode

import httpx

from app.core.config import get_settings
from app.scrapers.base import BaseScraper, ScrapedLead, ScraperRequest
from app.scrapers.cleaner import dedupe_leads
from app.scrapers.rate_limit import random_delay, retry_async


class GooglePlacesScraper(BaseScraper):
    """Google Places API adapter.

    This production-safe adapter uses Google's official Places API instead of browser
    automation against Google Maps pages. Set GOOGLE_PLACES_API_KEY in backend/.env.
    """

    source_name = "google_places"
    text_search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    async def scrape(self, request: ScraperRequest) -> list[ScrapedLead]:
        settings = get_settings()
        if not settings.google_places_api_key:
            raise RuntimeError("GOOGLE_PLACES_API_KEY is required for google_places source")

        query = f"{request.keyword} {request.location or ''}".strip()
        async with httpx.AsyncClient(timeout=30) as client:
            places = await self._text_search(client, query, settings.google_places_api_key)
            leads: list[ScrapedLead] = []
            for place in places[: request.max_results]:
                await random_delay()
                details = await self._details(client, place["place_id"], settings.google_places_api_key)
                leads.append(self._to_lead(place, details))
        return dedupe_leads(leads)

    async def _text_search(self, client: httpx.AsyncClient, query: str, api_key: str) -> list[dict]:
        async def do_request() -> list[dict]:
            url = f"{self.text_search_url}?{urlencode({'query': query, 'key': api_key})}"
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
            if payload.get("status") not in {"OK", "ZERO_RESULTS"}:
                raise RuntimeError(f"Google Places text search failed: {payload.get('status')}")
            return payload.get("results", [])

        return await retry_async(do_request)

    async def _details(self, client: httpx.AsyncClient, place_id: str, api_key: str) -> dict:
        fields = "name,formatted_phone_number,formatted_address,rating,user_ratings_total,website,place_id,types"

        async def do_request() -> dict:
            url = f"{self.details_url}?{urlencode({'place_id': place_id, 'fields': fields, 'key': api_key})}"
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
            if payload.get("status") != "OK":
                raise RuntimeError(f"Google Places details failed: {payload.get('status')}")
            return payload.get("result", {})

        return await retry_async(do_request)

    def _to_lead(self, place: dict, details: dict) -> ScrapedLead:
        return ScrapedLead(
            business_name=details.get("name") or place.get("name") or "Unknown Business",
            phone_number=details.get("formatted_phone_number"),
            address=details.get("formatted_address") or place.get("formatted_address"),
            rating=details.get("rating") or place.get("rating"),
            reviews_count=details.get("user_ratings_total") or place.get("user_ratings_total"),
            website=details.get("website"),
            extra_metadata={
                "source": self.source_name,
                "place_id": details.get("place_id") or place.get("place_id"),
                "types": details.get("types") or place.get("types", []),
            },
        )
