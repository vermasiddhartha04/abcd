from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Metadata(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True, index=True)

    ocr_result_id = Column(
        Integer,
        ForeignKey("ocr_results.id"),
        nullable=False,
        unique=True,
    )

    gstin = Column(String(20))
    pan = Column(String(20))

    taxpayer_name = Column(String(255))

    notice_number = Column(String(100))

    document_type = Column(String(100))

    section = Column(String(50))

    financial_year = Column(String(20))

    tax_period = Column(String(50))

    tax_amount = Column(Numeric(18, 2))

    interest = Column(Numeric(18, 2))

    penalty = Column(Numeric(18, 2))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    ocr_result = relationship("OCRResult")