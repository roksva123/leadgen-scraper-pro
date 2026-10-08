-- LeadGen Scraper Pro - PostgreSQL schema
-- Jalankan sebagai user postgres / user yang punya akses CREATE DATABASE.
-- Contoh via terminal dari folder backend:
--   psql -U postgres -f schema.sql
--
-- Jika password user postgres berbeda dari config app, update backend/.env:
--   DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5432/leadgen_scraper

-- Buat database kalau belum ada. Bagian ini memakai fitur psql \gexec.
SELECT 'CREATE DATABASE leadgen_scraper'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'leadgen_scraper'
)\gexec

\connect leadgen_scraper

-- Untuk UUID default gen_random_uuid().
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enum status job.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'job_status') THEN
        CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed');
    END IF;
END
$$;

-- Tabel job scraping.
CREATE TABLE IF NOT EXISTS scraping_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    target_source VARCHAR(100) NOT NULL,
    status job_status NOT NULL DEFAULT 'pending',
    total_scraped INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_scraping_jobs_keyword
    ON scraping_jobs (keyword);

CREATE INDEX IF NOT EXISTS ix_scraping_jobs_location
    ON scraping_jobs (location);

CREATE INDEX IF NOT EXISTS ix_scraping_jobs_target_source
    ON scraping_jobs (target_source);

-- Auto update kolom updated_at setiap row diubah.
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_scraping_jobs_updated_at ON scraping_jobs;
CREATE TRIGGER trg_scraping_jobs_updated_at
BEFORE UPDATE ON scraping_jobs
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- Tabel hasil lead.
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES scraping_jobs(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(80),
    address TEXT,
    rating DOUBLE PRECISION,
    reviews_count INTEGER,
    website VARCHAR(500),
    extra_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_leads_job_id
    ON leads (job_id);

CREATE INDEX IF NOT EXISTS ix_leads_business_name
    ON leads (business_name);

CREATE INDEX IF NOT EXISTS ix_leads_phone_number
    ON leads (phone_number);

-- Data test opsional: uncomment kalau mau isi contoh data.
-- INSERT INTO scraping_jobs (keyword, location, target_source, status, total_scraped)
-- VALUES ('restaurant', 'Jakarta', 'google_places', 'completed', 1)
-- RETURNING id;
--
-- INSERT INTO leads (job_id, business_name, phone_number, address, rating, reviews_count, website, extra_metadata)
-- VALUES (
--     '<ISI_UUID_JOB_DARI_QUERY_SEBELUMNYA>',
--     'Contoh Restaurant',
--     '+628123456789',
--     'Jakarta, Indonesia',
--     4.5,
--     120,
--     'https://example.com',
--     '{"source":"manual_seed"}'::jsonb
-- );
