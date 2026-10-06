from fastapi import APIRouter

from app.api.v1.export import router as export_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.leads import router as leads_router

api_router = APIRouter()
api_router.include_router(jobs_router)
api_router.include_router(leads_router)
api_router.include_router(export_router)
