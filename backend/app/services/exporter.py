from io import BytesIO, StringIO

import pandas as pd

from app.db.models import Lead


EXPORT_COLUMNS = [
    "business_name",
    "phone_number",
    "address",
    "rating",
    "reviews_count",
    "website",
    "extra_metadata",
]


def leads_to_dataframe(leads: list[Lead]) -> pd.DataFrame:
    rows = [
        {
            "business_name": lead.business_name,
            "phone_number": lead.phone_number,
            "address": lead.address,
            "rating": lead.rating,
            "reviews_count": lead.reviews_count,
            "website": lead.website,
            "extra_metadata": lead.extra_metadata,
        }
        for lead in leads
    ]
    return pd.DataFrame(rows, columns=EXPORT_COLUMNS)


def export_csv(leads: list[Lead]) -> bytes:
    buffer = StringIO()
    leads_to_dataframe(leads).to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8-sig")


def export_excel(leads: list[Lead]) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        leads_to_dataframe(leads).to_excel(writer, sheet_name="Leads", index=False)
    buffer.seek(0)
    return buffer.read()
