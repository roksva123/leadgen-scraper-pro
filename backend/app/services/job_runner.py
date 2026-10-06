import uuid

from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.db.models import JobStatus, Lead, ScrapingJob
from app.scrapers.base import ScraperRequest
from app.scrapers.registry import get_scraper


async def run_scraping_job(job_id: uuid.UUID, *, max_results: int) -> None:
    async with AsyncSessionLocal() as session:
        job = await session.get(ScrapingJob, job_id)
        if not job:
            return

        job.status = JobStatus.running
        job.error_message = None
        await session.commit()

        try:
            scraper = get_scraper(job.target_source)
            scraped = await scraper.scrape(
                ScraperRequest(keyword=job.keyword, location=job.location, max_results=max_results)
            )

            await session.execute(delete(Lead).where(Lead.job_id == job.id))
            for item in scraped:
                session.add(
                    Lead(
                        job_id=job.id,
                        business_name=item.business_name,
                        phone_number=item.phone_number,
                        address=item.address,
                        rating=item.rating,
                        reviews_count=item.reviews_count,
                        website=item.website,
                        extra_metadata=item.extra_metadata,
                    )
                )

            job.total_scraped = len(scraped)
            job.status = JobStatus.completed
            await session.commit()
        except Exception as exc:  # noqa: BLE001 - background jobs must persist failures
            job.status = JobStatus.failed
            job.error_message = str(exc)
            await session.commit()
