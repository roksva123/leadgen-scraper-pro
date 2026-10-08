# LeadGen Scraper Pro

LeadGen Scraper Pro adalah starter kit full-stack untuk menjalankan scraping lead bisnis, memantau status job, menyimpan hasil ke PostgreSQL, dan mengekspor data ke CSV atau Excel.

Aplikasi ini memakai backend FastAPI dan frontend React + Vite. Untuk pengembangan dan demo tersedia source `demo_directory` yang menghasilkan data contoh realistis. Untuk penggunaan data nyata, tersedia adapter `google_places` yang memakai Google Places API resmi.

## Fitur

- Dashboard web untuk membuat dan memantau scraping job.
- Background job runner untuk menjalankan proses scraping.
- Penyimpanan job dan lead di PostgreSQL.
- Pencarian dan filter lead berdasarkan job atau kata kunci.
- Export hasil lead ke CSV atau XLSX.
- Source scraper modular:
  - `demo_directory` untuk demo/development.
  - `google_places` untuk Google Places API resmi.
- Validasi request dan response dengan Pydantic.
- Migrasi database dengan Alembic.

## Tech Stack

### Backend

- Python 3.11+
- FastAPI
- SQLAlchemy Async
- PostgreSQL + asyncpg
- Alembic
- httpx
- pandas + openpyxl

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- lucide-react

## Struktur Project

```text
leadgen-scraper-pro/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Endpoint API
│   │   ├── core/            # Config dan database
│   │   ├── db/              # Model, schema, repository
│   │   ├── scrapers/        # Adapter scraper
│   │   └── services/        # Job runner dan exporter
│   ├── migrations/          # Alembic migrations
│   ├── .env.example
│   ├── alembic.ini
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/      # Komponen UI
    │   ├── lib/             # API client
    │   ├── types/           # TypeScript types
    │   └── App.tsx
    ├── .env.example
    ├── package.json
    └── vite.config.ts
```

## Prasyarat

Pastikan sudah terpasang:

- Python 3.11 atau lebih baru
- Node.js 18 atau lebih baru
- PostgreSQL
- npm

## Setup Backend

Masuk ke folder backend:

```bash
cd backend
```

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Git Bash / macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

Salin file environment:

```bash
cp .env.example .env
```

Jika memakai PowerShell:

```powershell
Copy-Item .env.example .env
```

Atur konfigurasi di `backend/.env`:

```env
APP_NAME="LeadGen Scraper Pro"
APP_ENV=development
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/leadgen_scraper
GOOGLE_PLACES_API_KEY=
SCRAPER_MIN_DELAY_SECONDS=1.0
SCRAPER_MAX_DELAY_SECONDS=3.0
SCRAPER_MAX_RETRIES=3
```

Buat database PostgreSQL sesuai `DATABASE_URL`, contoh:

```sql
CREATE DATABASE leadgen_scraper;
```

Jalankan migrasi database:

```bash
alembic upgrade head
```

Jalankan backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend akan berjalan di:

```text
http://localhost:8000
```

Health check:

```text
GET http://localhost:8000/health
```

## Setup Frontend

Masuk ke folder frontend:

```bash
cd frontend
```

Install dependency:

```bash
npm install
```

Salin file environment:

```bash
cp .env.example .env
```

Jika memakai PowerShell:

```powershell
Copy-Item .env.example .env
```

Isi `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Jalankan frontend:

```bash
npm run dev
```

Frontend akan berjalan di:

```text
http://localhost:5173
```

## Cara Pakai

1. Jalankan PostgreSQL.
2. Jalankan backend di port `8000`.
3. Jalankan frontend di port `5173`.
4. Buka dashboard di browser.
5. Buat scraping job baru dengan mengisi keyword, lokasi, source, dan jumlah hasil.
6. Tunggu job selesai.
7. Lihat data lead di tabel.
8. Export hasil ke CSV atau Excel jika diperlukan.

## Scraper Source

### `demo_directory`

Source default untuk development dan demo. Source ini tidak mengambil data dari website eksternal, melainkan membuat data lead contoh berdasarkan keyword dan lokasi.

Gunakan ini untuk:

- Demo produk.
- Testing UI.
- Testing flow job runner.
- Development tanpa API key.

### `google_places`

Source untuk mengambil data bisnis dari Google Places API resmi.

Untuk memakai source ini, isi variabel berikut di `backend/.env`:

```env
GOOGLE_PLACES_API_KEY=your_google_places_api_key
```

Catatan:

- Pastikan billing dan akses Google Places API sudah aktif di Google Cloud.
- Gunakan API sesuai Terms of Service penyedia data.
- Jangan memasukkan API key ke repository publik.

## Endpoint API

Base URL default:

```text
http://localhost:8000/api/v1
```

### Jobs

```text
POST /jobs/start
GET  /jobs
GET  /jobs/{job_id}
GET  /jobs/sources/available
```

Contoh request membuat job:

```json
{
  "keyword": "cafe",
  "location": "Jakarta",
  "target_source": "demo_directory",
  "max_results": 25
}
```

### Leads

```text
GET /leads
```

Query opsional:

- `job_id`
- `search`
- `limit`
- `offset`

### Export

```text
GET /export/{job_id}?format=excel
GET /export/{job_id}?format=csv
```

## Script Frontend

Dijalankan dari folder `frontend`:

```bash
npm run dev      # menjalankan Vite dev server
npm run build    # build production
npm run preview  # preview hasil build
npm run lint     # menjalankan ESLint
```

## Perintah Development Singkat

Terminal 1 - backend:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - frontend:

```bash
cd frontend
npm run dev
```

## Build Production

Build frontend:

```bash
cd frontend
npm run build
```

Untuk backend, jalankan server ASGI dengan Uvicorn atau server production lain sesuai environment deployment.

Contoh:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Frontend tidak bisa konek ke backend

Pastikan:

- Backend berjalan di `http://localhost:8000`.
- `VITE_API_BASE_URL` mengarah ke `http://localhost:8000/api/v1`.
- `BACKEND_CORS_ORIGINS` di backend berisi URL frontend, misalnya `http://localhost:5173`.

### Database error saat backend start

Pastikan:

- PostgreSQL sedang berjalan.
- Database `leadgen_scraper` sudah dibuat.
- `DATABASE_URL` sudah benar.
- Migrasi sudah dijalankan dengan `alembic upgrade head`.

### Source `google_places` gagal

Pastikan:

- `GOOGLE_PLACES_API_KEY` sudah diisi.
- Google Places API aktif.
- API key punya permission dan billing yang valid.

## Catatan Keamanan dan Kepatuhan

- Jangan commit file `.env` yang berisi credential atau API key.
- Gunakan source data dan API sesuai Terms of Service masing-masing penyedia.
- Hindari scraping agresif. Project ini sudah menyediakan delay dan retry agar request lebih terkendali.
- Untuk production, tambahkan autentikasi, rate limiting API, logging terstruktur, dan monitoring.

## Lisensi

Tambahkan lisensi sesuai kebutuhan project.
