import uuid

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Lead, ScrapingJob


async def create_job(session: AsyncSession, *, keyword: str, location: str | None, target_source: str) -> ScrapingJob:
    job = ScrapingJob(keyword=keyword, location=location, target_source=target_source)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


async def list_jobs(session: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[ScrapingJob]:
    result = await session.execute(
        select(ScrapingJob).order_by(ScrapingJob.created_at.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> ScrapingJob | None:
    return await session.get(ScrapingJob, job_id)


async def list_leads(
    session: AsyncSession,
    *,
    job_id: uuid.UUID | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Lead], int]:
    query: Select[tuple[Lead]] = select(Lead)
    count_query = select(func.count(Lead.id))

    filters = []
    if job_id:
        filters.append(Lead.job_id == job_id)
    if search:
        pattern = f"%{search}%"
        filters.append(or_(Lead.business_name.ilike(pattern), Lead.phone_number.ilike(pattern), Lead.address.ilike(pattern)))

    for condition in filters:
        query = query.where(condition)
        count_query = count_query.where(condition)

    total_result = await session.execute(count_query)
    total = int(total_result.scalar_one())

    rows = await session.execute(query.order_by(Lead.created_at.desc()).limit(limit).offset(offset))
    return list(rows.scalars().all()), total


async def get_job_leads(session: AsyncSession, job_id: uuid.UUID) -> list[Lead]:
    rows = await session.execute(select(Lead).where(Lead.job_id == job_id).order_by(Lead.created_at.asc()))
    return list(rows.scalars().all())
