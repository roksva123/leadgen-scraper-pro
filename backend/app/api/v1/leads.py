import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.db.repositories import list_leads
from app.db.schemas import LeadRead, PaginatedLeads

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=PaginatedLeads)
async def get_leads(
    session: AsyncSession = Depends(get_db_session),
    job_id: uuid.UUID | None = None,
    search: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> PaginatedLeads:
    leads, total = await list_leads(session, job_id=job_id, search=search, limit=limit, offset=offset)
    return PaginatedLeads(
        items=[LeadRead.model_validate(lead) for lead in leads],
        total=total,
        limit=limit,
        offset=offset,
    )
