from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UploadBase(BaseModel):
    case_id: int


class UploadCreate(UploadBase):
    pass


class UploadResponse(UploadBase):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_path: str
    uploaded_by: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )