import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.core.config import get_settings

T = TypeVar("T")


async def random_delay() -> None:
    settings = get_settings()
    await asyncio.sleep(random.uniform(settings.scraper_min_delay_seconds, settings.scraper_max_delay_seconds))


async def retry_async(fn: Callable[[], Awaitable[T]], *, attempts: int | None = None) -> T:
    settings = get_settings()
    max_attempts = attempts or settings.scraper_max_retries
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await fn()
        except Exception as exc:  # noqa: BLE001 - stored and retried intentionally
            last_error = exc
            if attempt == max_attempts:
                break
            await asyncio.sleep(min(2**attempt, 10))
    assert last_error is not None
    raise last_error
