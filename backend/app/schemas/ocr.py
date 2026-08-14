from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OCRResultResponse(BaseModel):
    id: int
    upload_id: int
    extracted_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)