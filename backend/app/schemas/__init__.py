from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    Token,
)

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserUpdate,
)

from app.schemas.case import (
    CaseBase,
    CaseCreate,
    CaseUpdate,
    CaseResponse,
)

from app.schemas.upload import (
    UploadCreate,
    UploadResponse,
)

from app.schemas.ocr import (
    OCRResultResponse,
)

from app.schemas.metadata import (
    MetadataResponse,
)

from app.schemas.analysis import (
    AnalysisResponse,
)

from app.schemas.reply import (
    ReplyResponse,
)

from app.schemas.dashboard import (
    DashboardSummary,
)

__all__ = [
    # ==========================
    # Authentication
    # ==========================
    "LoginRequest",
    "RegisterRequest",
    "Token",

    # ==========================
    # User
    # ==========================
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserUpdate",

    # ==========================
    # Case
    # ==========================
    "CaseBase",
    "CaseCreate",
    "CaseUpdate",
    "CaseResponse",

    # ==========================
    # Upload
    # ==========================
    "UploadCreate",
    "UploadResponse",

    # ==========================
    # OCR
    # ==========================
    "OCRResultResponse",

    # ==========================
    # Metadata
    # ==========================
    "MetadataResponse",

    # ==========================
    # Analysis
    # ==========================
    "AnalysisResponse",

    # ==========================
    # Reply
    # ==========================
    "ReplyResponse",

    # ==========================
    # Dashboard
    # ==========================
    "DashboardSummary",
]