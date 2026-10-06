import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.db.models import JobStatus


class JobCreate(BaseModel):
    keyword: str = Field(min_length=2, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    target_source: str = Field(default="demo_directory", max_length=100)
    max_results: int = Field(default=25, ge=1, le=200)


class JobRead(BaseModel):
    id: uuid.UUID
    keyword: str
    location: str | None
    target_source: str
    status: JobStatus
    total_scraped: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadRead(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    business_name: str
    phone_number: str | None
    address: str | None
    rating: float | None
    reviews_count: int | None
    website: str | None
    extra_metadata: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedLeads(BaseModel):
    items: list[LeadRead]
    total: int
    limit: int
    offset: int


class ExportFormat(BaseModel):
    format: Literal["excel", "csv"] = "excel"
