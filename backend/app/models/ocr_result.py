from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    upload_id = Column(
        Integer,
        ForeignKey("uploads.id"),
        nullable=False,
    )

    extracted_text = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    upload = relationship("Upload")