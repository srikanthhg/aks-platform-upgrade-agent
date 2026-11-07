from __future__ import annotations

import shutil
from contextlib import asynccontextmanager
from typing import AsyncIterator

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config import get_settings
from graph.checkpointer import create_checkpointer
from graph.nodes import initialize_node_dependencies
from graph.workflow import build_workflow
from services.job_queue import JobQueue
from services.locks import ClusterLockStore
from services.workflow_service import WorkflowService
from tools.logger import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("AKS Upgrade Agent API starting in %s mode", settings.app_environment)
    connection = None
    try:
        queue = JobQueue(settings.database_url)
        lock_store = ClusterLockStore(settings.database_url)

        # All database-backed schemas are initialized after the process starts,
        # never as a side effect of importing Python modules.
        queue.initialize()
        lock_store.initialize()
        initialize_node_dependencies()
        connection, checkpointer = create_checkpointer(settings.database_url)
        graph = build_workflow(checkpointer)
        app.state.workflow_service = WorkflowService(
            graph=graph, lock_store=lock_store, queue=queue
        )
        logger.info("PostgreSQL dependencies and LangGraph initialized")
        yield
    except Exception:
        logger.exception("API startup or runtime failed while using PostgreSQL")
        raise
    finally:
        app.state.workflow_service = None
        if connection is not None:
            connection.close()
        logger.info("AKS Upgrade Agent API stopped")


app = FastAPI(title="AKS Upgrade Agent API", version="4.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)
app.include_router(router, prefix="/api/v1", tags=["workflows"])


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    try:
        with psycopg.connect(settings.database_url, connect_timeout=5) as connection:
            connection.execute("SELECT 1").fetchone()
    except Exception as exc:
        raise HTTPException(503, f"PostgreSQL is not ready: {exc}") from exc
    return {"status": "ready"}


@app.get("/diagnostics")
def diagnostics():
    return {
        "environment": settings.app_environment,
        "auth_mode": settings.auth_mode,
        "allow_real_upgrades": settings.allow_real_upgrades,
        "default_dry_run": settings.default_dry_run,
        "ai_advisor_enabled": settings.ai_enabled,
        "ai_provider": "Azure OpenAI" if settings.ai_enabled else None,
        "database": "postgresql",
        "az_available": shutil.which("az") is not None,
        "kubectl_available": shutil.which("kubectl") is not None,
        "kubelogin_available": shutil.which("kubelogin") is not None,
        "multi_replica_supported": True,
    }
