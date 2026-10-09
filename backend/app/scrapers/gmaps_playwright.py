import asyncio
import re
import sys
from urllib.parse import quote_plus

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError, async_playwright

from app.scrapers.base import BaseScraper, ScrapedLead, ScraperRequest
from app.scrapers.cleaner import dedupe_leads


REVIEW_COUNT_PATTERN = re.compile(r"([\d.,]+)\s*(rb|ribu|k|m|jt|juta|million)?", re.IGNORECASE)


async def scrape_gmaps_playwright(keyword: str, location: str, max_results: int) -> list[ScrapedLead]:
    """Scrape Google Maps search results using Playwright browser automation."""

    if _needs_windows_playwright_thread():
        return await asyncio.to_thread(_run_in_windows_proactor_loop, keyword, location, max_results)

    return await _scrape_gmaps_playwright(keyword, location, max_results)


async def _scrape_gmaps_playwright(keyword: str, location: str, max_results: int) -> list[ScrapedLead]:
    query = f"{keyword} di {location}" if location else keyword
    search_url = f"https://www.google.com/maps/search/{quote_plus(query)}"

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context(locale="en-US")
            page = await context.new_page()

            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=60_000)
                await _accept_cookie_dialog(page)
                await page.wait_for_timeout(3_000)

                result_urls = await _collect_result_urls(page, max_results)
                if not result_urls and "/maps/place/" in page.url:
                    result_urls = [page.url]

                leads: list[ScrapedLead] = []
                for url in result_urls[:max_results]:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                    await page.wait_for_timeout(2_000)
                    lead = await _extract_place_details(page)
                    if lead.business_name:
                        leads.append(lead)

                return dedupe_leads(leads)
            finally:
                await context.close()
                await browser.close()
    except PlaywrightError as exc:
        message = str(exc)
        if "Executable doesn't exist" in message or "playwright install" in message.lower():
            raise RuntimeError("Playwright browser is not installed. Run: playwright install chromium") from exc
        raise


def _needs_windows_playwright_thread() -> bool:
    if sys.platform != "win32":
        return False

    try:
        loop = asyncio.get_running_loop()
        return not isinstance(loop, asyncio.ProactorEventLoop)
    except AttributeError:
        return False


def _run_in_windows_proactor_loop(keyword: str, location: str, max_results: int) -> list[ScrapedLead]:
    loop = asyncio.ProactorEventLoop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(_scrape_gmaps_playwright(keyword, location, max_results))
    finally:
        asyncio.set_event_loop(None)
        loop.close()


class GMapsPlaywrightScraper(BaseScraper):
    """Free Google Maps scraper that uses Playwright instead of the paid Places API."""

    source_name = "gmaps_playwright"

    async def scrape(self, request: ScraperRequest) -> list[ScrapedLead]:
        return await scrape_gmaps_playwright(
            keyword=request.keyword,
            location=request.location or "",
            max_results=request.max_results,
        )


async def _accept_cookie_dialog(page: Page) -> None:
    labels = [
        "Accept all",
        "I agree",
        "Agree",
        "Terima semua",
        "Saya setuju",
        "Setuju",
    ]
    for label in labels:
        button = page.get_by_role("button", name=re.compile(label, re.IGNORECASE))
        try:
            if await button.count():
                await button.first.click(timeout=2_000)
                await page.wait_for_timeout(1_000)
                return
        except PlaywrightError:
            continue


async def _collect_result_urls(page: Page, max_results: int) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    stable_scrolls = 0

    for _ in range(40):
        await _store_visible_result_urls(page, urls, seen)
        if len(urls) >= max_results:
            break

        before_count = len(urls)
        if await _scroll_results_panel(page):
            await page.wait_for_timeout(1_500)
        else:
            break

        await _store_visible_result_urls(page, urls, seen)
        if len(urls) == before_count:
            stable_scrolls += 1
        else:
            stable_scrolls = 0

        if stable_scrolls >= 5:
            break

    return urls


async def _store_visible_result_urls(page: Page, urls: list[str], seen: set[str]) -> None:
    links = page.locator('a[href*="/maps/place/"]')
    count = min(await links.count(), 100)
    for index in range(count):
        href = await links.nth(index).get_attribute("href")
        if not href:
            continue
        clean_href = href.split("&ved=")[0]
        if clean_href in seen:
            continue
        seen.add(clean_href)
        urls.append(clean_href)


async def _scroll_results_panel(page: Page) -> bool:
    feed = page.locator('[role="feed"]').first
    try:
        if await feed.count():
            await feed.hover(timeout=2_000)
            await page.mouse.wheel(0, 5_000)
            return True
    except PlaywrightError:
        pass

    try:
        await page.mouse.wheel(0, 5_000)
        return True
    except PlaywrightError:
        return False


async def _extract_place_details(page: Page) -> ScrapedLead:
    business_name = await _first_text(page, ["h1.DUwDvf", "h1"])
    phone = await _phone_number(page)
    address = await _first_text(
        page,
        [
            '[data-item-id="address"] .Io6YTe',
            '[data-item-id="address"]',
            'button[aria-label^="Address:"]',
            'button[aria-label^="Alamat:"]',
        ],
    )
    rating = _parse_rating(await _first_text(page, ["span.MW4etd", "div.F7nice span[aria-hidden='true']"]))
    reviews_count = _parse_reviews_count(
        await _first_attribute(
            page,
            [
                'button[aria-label*="reviews"]',
                'button[aria-label*="Reviews"]',
                'button[aria-label*="ulasan"]',
                'button[aria-label*="Ulasan"]',
            ],
            "aria-label",
        )
        or await _first_text(page, ["span.UY7F9", "div.F7nice"])
    )
    website = await _first_attribute(page, ['a[data-item-id="authority"]'], "href")

    return ScrapedLead(
        business_name=business_name or "Unknown Business",
        phone_number=phone,
        address=_strip_label(address, ["Address", "Alamat"]),
        rating=rating,
        reviews_count=reviews_count,
        website=website,
        extra_metadata={"source": GMapsPlaywrightScraper.source_name, "maps_url": page.url},
    )


async def _phone_number(page: Page) -> str | None:
    data_item = await _first_attribute(page, ['button[data-item-id^="phone:tel:"]'], "data-item-id")
    if data_item and data_item.startswith("phone:tel:"):
        return data_item.removeprefix("phone:tel:")

    phone_text = await _first_text(
        page,
        [
            'button[data-item-id^="phone:tel:"] .Io6YTe',
            'button[data-item-id^="phone:tel:"]',
            'button[aria-label^="Phone:"]',
            'button[aria-label^="Telepon:"]',
            'button[aria-label^="Nomor telepon:"]',
        ],
    )
    return _strip_label(phone_text, ["Phone", "Telepon", "Nomor telepon"])


async def _first_text(page: Page, selectors: list[str]) -> str | None:
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if await locator.count():
                text = (await locator.inner_text(timeout=2_000)).strip()
                if text:
                    return text
        except (PlaywrightError, PlaywrightTimeoutError):
            continue
    return None


async def _first_attribute(page: Page, selectors: list[str], attribute: str) -> str | None:
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if await locator.count():
                value = await locator.get_attribute(attribute, timeout=2_000)
                if value:
                    return value.strip()
        except (PlaywrightError, PlaywrightTimeoutError):
            continue
    return None


def _strip_label(value: str | None, labels: list[str]) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    for label in labels:
        cleaned = re.sub(rf"^{re.escape(label)}\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned or None


def _parse_rating(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"\d+(?:[,.]\d+)?", value)
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def _parse_reviews_count(value: str | None) -> int | None:
    if not value:
        return None

    match = REVIEW_COUNT_PATTERN.search(value.replace("(", "").replace(")", ""))
    if not match:
        return None

    number_text, suffix = match.groups()
    normalized_number = number_text.replace(".", "").replace(",", ".")
    try:
        number = float(normalized_number)
    except ValueError:
        return None

    multiplier = 1
    if suffix:
        suffix = suffix.lower()
        if suffix in {"k", "rb", "ribu"}:
            multiplier = 1_000
        elif suffix in {"m", "jt", "juta", "million"}:
            multiplier = 1_000_000

    return int(number * multiplier)
