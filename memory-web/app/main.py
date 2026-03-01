"""
MemoryWeb FastAPI application — port 8100.
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from .config import settings
from .database import ensure_schema_and_extensions, engine
from .models import Base
from .routers import ingest, memory, retention, search, status
from .workers import embedding_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: ensure schema, extensions, tables, and background workers."""
    logger.info("MemoryWeb starting on port %d", settings.MW_PORT)
    try:
        ensure_schema_and_extensions()
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema ready")
    except Exception as e:
        logger.error("DB startup failed: %s", e)

    # Start background embedding worker
    embedding_worker.start_worker()
    logger.info("Embedding worker started")

    # Preload sentence-transformers model so Tier 3 first query is fast
    try:
        from .services import retrieval as _retrieval
        _retrieval.warmup_model()
        logger.info("Sentence-transformers model warmed up (%s)", settings.MW_EMBED_MODEL)
    except Exception as e:
        logger.warning("Model warmup failed (Tier 3 first query will be slow): %s", e)

    yield

    # Graceful shutdown
    embedding_worker.stop_worker()
    logger.info("MemoryWeb shutting down")


app = FastAPI(
    title="MemoryWeb",
    description="Provenance-Aware Tiered Memory System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(status.router)
app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(memory.router)
app.include_router(retention.router)


@app.get("/", tags=["root"])
def root():
    dashboard = Path(__file__).parent.parent / "static" / "dashboard.html"
    if dashboard.exists():
        return FileResponse(str(dashboard), media_type="text/html")
    return {"service": "MemoryWeb", "version": "0.1.0", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.MW_PORT,
        reload=False,
        log_level="info",
    )
