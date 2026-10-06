import re
from collections.abc import Iterable

from app.scrapers.base import ScrapedLead


PHONE_KEEP_PATTERN = re.compile(r"[^0-9+]")


def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    cleaned = PHONE_KEEP_PATTERN.sub("", phone)
    return cleaned or None


def dedupe_leads(leads: Iterable[ScrapedLead]) -> list[ScrapedLead]:
    seen: set[tuple[str, str | None]] = set()
    unique: list[ScrapedLead] = []
    for lead in leads:
        lead.phone_number = normalize_phone(lead.phone_number)
        key = (lead.business_name.strip().lower(), lead.phone_number)
        if key in seen:
            continue
        seen.add(key)
        unique.append(lead)
    return unique
