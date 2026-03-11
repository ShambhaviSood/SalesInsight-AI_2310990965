"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging_config import setup_logging

settings = get_settings()
setup_logging(debug=settings.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A quick-response tool that lets sales team members upload CSV/Excel "
        "sales data and receive an AI-generated executive summary via email."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    logger.info(
        "Starting %s v%s (env=%s)",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.ENVIRONMENT,
    )
