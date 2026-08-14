from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnalysisResponse(BaseModel):
    id: int
    metadata_id: int

    document_type: str | None = None
    summary: str | None = None
    risk_level: str | None = None
    reply_required: bool = True
    recommendation: str | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)