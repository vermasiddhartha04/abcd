from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AnalysisResponse(BaseModel):
    id: int
    metadata_id: int

    document_type: str | None = None
    summary: str | None = None
    risk_level: str | None = None
    reply_required: bool = True
    recommendation: str | None = None

    # Structured litigation extraction
    demands: list[dict[str, Any]] | None = None

    penalty_proposals: list[dict[str, Any]] | None = None

    allegations: list[dict[str, Any]] | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)