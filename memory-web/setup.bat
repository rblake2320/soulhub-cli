@echo off
REM MemoryWeb Setup Script for Windows
REM Run from D:\memory-web

echo === MemoryWeb Setup ===
echo.

REM 1. Create and activate venv
echo [1/6] Creating Python virtual environment...
C:\Python312\python.exe -m venv .venv
call .venv\Scripts\activate.bat

REM 2. Install dependencies
echo [2/6] Installing dependencies...
pip install -e ".[dev]"

REM 3. Start Redis via Docker
echo [3/6] Starting Redis...
docker run -d --name memoryweb-redis -p 6379:6379 redis:7-alpine 2>nul || echo Redis already running

REM 4. Install pgvector (manual step reminder)
echo [4/6] pgvector check...
python scripts/setup_pgvector.py

REM 5. Run Alembic migration
echo [5/6] Running database migration...
alembic upgrade head

REM 6. Verify
echo [6/6] Running verification...
python -c "from app.database import ensure_schema_and_extensions; ensure_schema_and_extensions(); print('DB OK')"

echo.
echo === Setup complete! ===
echo.
echo Start API server:    uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
echo Start Celery worker: celery -A app.celery_app worker --loglevel=info -P threads
echo Seed from sessions:  python scripts/seed_from_sessions.py --all --pipeline
echo.
