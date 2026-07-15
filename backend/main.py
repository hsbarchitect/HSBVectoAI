"""
HSBVectoAI Backend — FastAPI Application Entry Point
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import create_tables
from routers import auth_router, license_router, ai_router, stripe_router

settings = get_settings()
logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HSBVectoAI API",
    description="AI-powered CorelDRAW assistant backend — auth, licensing, AI proxy, payments.",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,   # Hide Swagger in production
    redoc_url="/redoc" if settings.debug else None,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(license_router)
app.include_router(ai_router)
app.include_router(stripe_router)


# ── Lifecycle ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("HSBVectoAI Backend starting up...")
    try:
        await create_tables()
        logger.info("Database tables verified.")
    except Exception as e:
        logger.warning("DB connection failed on startup (will retry on first request): %s", e)


@app.get("/health", tags=["system"])
async def health():
    """Health check endpoint — used by Cloud Run and load balancers."""
    return {"status": "ok", "app": settings.app_name}
