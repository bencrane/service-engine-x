"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.cal import router as cal_router
from app.routers.health import router as health_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Service Engine X — webhook ingestion service",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(cal_router)
