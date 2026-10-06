"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    job_status = postgresql.ENUM("pending", "running", "completed", "failed", name="job_status")
    job_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "scraping_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("target_source", sa.String(length=100), nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("total_scraped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scraping_jobs_keyword", "scraping_jobs", ["keyword"])
    op.create_index("ix_scraping_jobs_location", "scraping_jobs", ["location"])
    op.create_index("ix_scraping_jobs_target_source", "scraping_jobs", ["target_source"])

    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_name", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=80), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("reviews_count", sa.Integer(), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["scraping_jobs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_leads_job_id", "leads", ["job_id"])
    op.create_index("ix_leads_business_name", "leads", ["business_name"])
    op.create_index("ix_leads_phone_number", "leads", ["phone_number"])


def downgrade() -> None:
    op.drop_index("ix_leads_phone_number", table_name="leads")
    op.drop_index("ix_leads_business_name", table_name="leads")
    op.drop_index("ix_leads_job_id", table_name="leads")
    op.drop_table("leads")
    op.drop_index("ix_scraping_jobs_target_source", table_name="scraping_jobs")
    op.drop_index("ix_scraping_jobs_location", table_name="scraping_jobs")
    op.drop_index("ix_scraping_jobs_keyword", table_name="scraping_jobs")
    op.drop_table("scraping_jobs")
    postgresql.ENUM(name="job_status").drop(op.get_bind(), checkfirst=True)
