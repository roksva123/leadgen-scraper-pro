import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.db.repositories import get_job, get_job_leads
from app.services.exporter import export_csv, export_excel

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/{job_id}")
async def export_job(
    job_id: uuid.UUID,
    format: str = Query(default="excel", pattern="^(excel|csv)$"),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    job = await get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    leads = await get_job_leads(session, job_id)
    safe_keyword = "".join(ch for ch in job.keyword.lower().replace(" ", "-") if ch.isalnum() or ch == "-")

    if format == "csv":
        content = export_csv(leads)
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{safe_keyword}-leads.csv"'},
        )

    content = export_excel(leads)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{safe_keyword}-leads.xlsx"'},
    )
