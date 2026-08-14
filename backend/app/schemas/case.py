from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CaseBase(BaseModel):
    case_no: str
    gstin: str
    taxpayer_name: str
    notice_type: str
    financial_year: str
    status: str = "Pending"


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    case_no: Optional[str] = None
    gstin: Optional[str] = None
    taxpayer_name: Optional[str] = None
    notice_type: Optional[str] = None
    financial_year: Optional[str] = None
    status: Optional[str] = None


class CaseResponse(CaseBase):
    id: int
    uploaded_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)