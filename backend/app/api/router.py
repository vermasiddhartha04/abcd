from fastapi import APIRouter

from app.api.upload import router as upload_router
from app.api.ocr import router as ocr_router
from app.api.metadata import router as metadata_router
from app.api.analysis import router as analysis_router
from app.api.reply import router as reply_router
from app.api.process import router as process_router

from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.documents import router as documents_router
from app.api.dashboard import router as dashboard_router


# ==========================================================
# API V1 ROUTER
# ==========================================================

api_router = APIRouter()


# ==========================================================
# AUTH
# ==========================================================

api_router.include_router(
    auth_router
)


# ==========================================================
# CASES
# ==========================================================

api_router.include_router(
    cases_router
)


# ==========================================================
# DOCUMENTS
# ==========================================================

api_router.include_router(
    documents_router
)


# ==========================================================
# UPLOAD
# ==========================================================

api_router.include_router(
    upload_router
)


# ==========================================================
# OCR
# ==========================================================

api_router.include_router(
    ocr_router
)


# ==========================================================
# GST METADATA
# ==========================================================

api_router.include_router(
    metadata_router
)


# ==========================================================
# AI ANALYSIS
# ==========================================================

api_router.include_router(
    analysis_router
)


# ==========================================================
# AI REPLY
# ==========================================================

api_router.include_router(
    reply_router
)


# ==========================================================
# DASHBOARD
# ==========================================================

api_router.include_router(
    dashboard_router
)


# ==========================================================
# COMPLETE DOCUMENT PROCESSING
#
# PDF
#  ↓
# Upload
#  ↓
# OCR
#  ↓
# Metadata
#  ↓
# Analysis
#  ↓
# AI Reply
#
# Endpoint:
# POST /api/v1/process/{upload_id}
# ==========================================================

api_router.include_router(
    process_router
)
