"""
File: app/main.py
Purpose: FastAPI application factory and entry point.
Responsibilities:
  - Create the FastAPI app instance
  - Configure CORS middleware (allow frontend origin)
  - Mount the /api/v1 router
  - Add health check endpoint
  - Initialize ChromaDB knowledge base on startup
Dependencies:
  - fastapi
  - app.api.v1.router (api_router)
  - app.core.config (settings)
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.limiter import limiter


def _load_rag_in_background() -> None:
    """
    Purpose: Load RAG knowledge base synchronously (called in a thread).
    Runs in a background thread so it never blocks the event loop.
    """
    try:
        from app.rag.knowledge_loader import load_knowledge_base
        load_knowledge_base()
        print("✅ RAG knowledge base initialized")
    except Exception as e:
        print(f"⚠️  RAG initialization failed (non-fatal): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Purpose: Handle application startup and shutdown events.
    Startup:
      - Kick off RAG loading in a background thread (non-blocking)
      - Server starts accepting requests immediately
    Shutdown:
      - Clean up resources if needed
    """
    # ── Startup ────────────────────────────────────────────────────────────────
    print(f"🚀 Starting {settings.app_name} API [{settings.app_env}]")

    # Run RAG initialization in a thread — server starts immediately without waiting
    asyncio.get_event_loop().run_in_executor(None, _load_rag_in_background)

    yield

    # ── Shutdown ───────────────────────────────────────────────────────────────
    print("Shutting down FounderOS API")


def create_app() -> FastAPI:
    """
    Purpose: Create and configure the FastAPI application instance.
    Returns:
      FastAPI: Configured application ready to serve.
    """
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered startup planning platform — from idea to execution blueprint",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Rate limiter — attach state and exception handler ─────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ── CORS — allow only the frontend origin ─────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url, "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ─────────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ── Health check ───────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="API health check")
    async def health_check():
        return {"status": "ok", "service": settings.app_name}

    return app


# Module-level app instance — used by uvicorn
app = create_app()
