@echo off
REM Start MemoryWeb API + Celery worker
REM Run from D:\memory-web

call .venv\Scripts\activate.bat

echo Starting Celery worker in background...
start "MemoryWeb-Celery" cmd /k "celery -A app.celery_app worker --loglevel=info -P threads -c 4"

echo Waiting 3 seconds for worker to start...
timeout /t 3 /nobreak > nul

echo Starting FastAPI server on port 8100...
uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload --log-level info
