from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logger import logger

logger.info("GST Litigation AI Backend Started")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    default_response_class=ORJSONResponse,
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    global_exception_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Version 1
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    logger.info("Root endpoint accessed")

    return {
        "status": "success",
        "message": "GST Litigation AI Backend Running",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health():
    logger.info("Health endpoint accessed")

    return {
        "status": "healthy"
    }