"""Ingest API routes."""

from typing import List, Optional

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..celery_app import celery_app
from ..deps import get_db
from ..models import Source
from ..schemas import (
    IngestAllSessionsRequest,
    IngestSessionRequest,
    IngestSharedChatRequest,
    IngestSqliteMemoryRequest,
    IngestStatusResponse,
    SourceOut,
    TaskResponse,
)
from ..tasks.ingest_tasks import (
    ingest_all_sessions_task,
    ingest_session_task,
    ingest_shared_chat_task,
    ingest_sqlite_memory_task,
)
from ..tasks.pipeline_tasks import run_full_pipeline

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/session", response_model=TaskResponse)
def ingest_session(body: IngestSessionRequest):
    """Ingest one Claude session JSONL file asynchronously."""
    task = ingest_session_task.delay(body.path, body.force)
    # Chain with pipeline
    run_full_pipeline.apply_async(countdown=2, kwargs={"source_id": -1})  # placeholder
    return TaskResponse(task_id=task.id, status="queued", message=f"Ingesting {body.path}")


@router.post("/session/all", response_model=TaskResponse)
def ingest_all_sessions(body: IngestAllSessionsRequest):
    """Ingest all session JSONLs in directory."""
    task = ingest_all_sessions_task.delay(body.directory, body.force)
    return TaskResponse(task_id=task.id, status="queued", message="Ingesting all sessions")


@router.post("/shared-chat", response_model=TaskResponse)
def ingest_shared_chat(body: IngestSharedChatRequest):
    """Ingest AI Army shared chat markdown files."""
    task = ingest_shared_chat_task.delay(body.directory, body.limit, body.force)
    return TaskResponse(task_id=task.id, status="queued", message="Ingesting shared chat")


@router.post("/sqlite-memory", response_model=TaskResponse)
def ingest_sqlite_memory(body: IngestSqliteMemoryRequest):
    """Import existing SQLite memory.db."""
    task = ingest_sqlite_memory_task.delay(body.path)
    return TaskResponse(task_id=task.id, status="queued", message="Importing SQLite memory")


@router.get("/status/{task_id}", response_model=IngestStatusResponse)
def get_ingest_status(task_id: str):
    """Poll status of an async ingest task."""
    result = AsyncResult(task_id, app=celery_app)
    info = result.info or {}
    return IngestStatusResponse(
        task_id=task_id,
        status=result.status,
        stage=info.get("stage") if isinstance(info, dict) else None,
        records_processed=info.get("records_processed") if isinstance(info, dict) else None,
        error=str(info) if result.status == "FAILURE" else None,
        result=info if result.status == "SUCCESS" and isinstance(info, dict) else None,
    )


@router.get("/sources", response_model=List[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    """List all ingested sources."""
    sources = db.query(Source).order_by(Source.ingested_at.desc()).all()
    return sources


@router.post("/pipeline/{source_id}", response_model=TaskResponse)
def run_pipeline(source_id: int):
    """Manually trigger the full processing pipeline for a source."""
    task = run_full_pipeline.delay(source_id)
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Pipeline started for source {source_id}",
    )
