from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MetadataBase(BaseModel):
    gstin: Optional[str] = None
    pan: Optional[str] = None

    vendor: Optional[str] = None
    vendor_gstin: Optional[str] = None

    taxpayer_name: Optional[str] = None
    notice_number: Optional[str] = None
    document_type: Optional[str] = None
    section: Optional[str] = None
    financial_year: Optional[str] = None
    tax_period: Optional[str] = None
    tax_amount: Optional[Decimal] = None
    interest: Optional[Decimal] = None
    penalty: Optional[Decimal] = None


class MetadataResponse(MetadataBase):
    id: int
    ocr_result_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )