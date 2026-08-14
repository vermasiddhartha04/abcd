from typing import Any, Optional

from pydantic import BaseModel


class ProcessDocumentResponse(BaseModel):

    success: bool

    upload_id: int

    ocr_result_id: int

    metadata_id: int

    analysis_id: int

    reply_id: Optional[int] = None

    document: dict[str, Any]

    metadata: dict[str, Any]

    analysis: dict[str, Any]

    reply: Optional[dict[str, Any]] = None

    litigation: Optional[dict[str, Any]] = None