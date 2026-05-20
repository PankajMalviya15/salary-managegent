"""
FastAPI application entrypoint.

Configures CORS, structured error handling, request logging,
includes all routers under /api/v1, and exposes a /health endpoint.
"""

import os
import time
import logging
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

load_dotenv()

from app.routers import employees, analytics, lookups  # noqa: E402

# ── Logging ────────────────────────────────────────────────────────

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("salary_api")

# ── App ────────────────────────────────────────────────────────────

app = FastAPI(
    title="Salary Management API",
    description="Backend API for managing employee records and compensation analytics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Logging Middleware (7.2) ───────────────────────────────

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log method, path, status code, and duration for every request."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s → %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ── Structured Error Handling (7.1) ────────────────────────────────

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors (duplicate email, invalid FK)."""
    detail = str(exc.orig) if exc.orig else str(exc)

    # Detect duplicate email
    if "UNIQUE constraint failed" in detail and "email" in detail:
        return JSONResponse(
            status_code=409,
            content={"detail": "An employee with this email address already exists."},
        )

    # Detect FK violations
    if "FOREIGN KEY constraint failed" in detail:
        return JSONResponse(
            status_code=422,
            content={"detail": "Referenced job title or department does not exist."},
        )

    # Generic integrity error
    logger.error("IntegrityError: %s", detail)
    return JSONResponse(
        status_code=409,
        content={"detail": "A database constraint was violated."},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler: log traceback, return sanitised 500."""
    logger.error(
        "Unhandled exception on %s %s:\n%s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# ── Routers ────────────────────────────────────────────────────────

app.include_router(employees.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(lookups.router, prefix="/api/v1")


# ── Health ─────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
