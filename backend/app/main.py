"""
FastAPI application entrypoint.

Configures CORS, includes all routers under /api/v1,
and exposes a /health endpoint.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.routers import employees, analytics, lookups  # noqa: E402

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

# ── Routers ────────────────────────────────────────────────────────

app.include_router(employees.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(lookups.router, prefix="/api/v1")


# ── Health ─────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
