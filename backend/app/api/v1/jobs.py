import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.db.repositories import create_job, get_job, list_jobs
from app.db.schemas import JobCreate, JobRead
from app.scrapers.registry import list_sources
from app.services.job_runner import run_scraping_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/start", response_model=JobRead, status_code=201)
async def start_job(
    payload: JobCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
) -> JobRead:
    if payload.target_source not in list_sources():
        raise HTTPException(status_code=400, detail={"message": "Unsupported target_source", "sources": list_sources()})

    job = await create_job(
        session,
        keyword=payload.keyword,
        location=payload.location,
        target_source=payload.target_source,
    )
    background_tasks.add_task(run_scraping_job, job.id, max_results=payload.max_results)
    return JobRead.model_validate(job)


@router.get("", response_model=list[JobRead])
async def get_jobs(
    session: AsyncSession = Depends(get_db_session),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[JobRead]:
    jobs = await list_jobs(session, limit=limit, offset=offset)
    return [JobRead.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobRead)
async def get_job_by_id(job_id: uuid.UUID, session: AsyncSession = Depends(get_db_session)) -> JobRead:
    job = await get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobRead.model_validate(job)


@router.get("/sources/available", response_model=list[str])
async def get_sources() -> list[str]:
    return list_sources()
