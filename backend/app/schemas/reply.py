from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReplyResponse(BaseModel):
    id: int
    analysis_id: int
    draft_reply: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)