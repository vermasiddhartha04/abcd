from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    metadata_id = Column(
        Integer,
        ForeignKey("metadata.id"),
        nullable=False,
        unique=True,
    )

    document_type = Column(String(100))

    summary = Column(Text)

    risk_level = Column(String(20))

    reply_required = Column(
        Boolean,
        default=True,
    )

    recommendation = Column(Text)

    # Structured litigation extraction
    demands = Column(
        JSON,
        nullable=True,
    )

    penalty_proposals = Column(
        JSON,
        nullable=True,
    )

    allegations = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Don't use "metadata" as relationship name
    metadata_record = relationship("Metadata")
    