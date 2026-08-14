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


class Reply(Base):
    __tablename__ = "replies"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    analysis_id = Column(
        Integer,
        ForeignKey("analysis.id"),
        nullable=False,
        unique=True,
    )

    draft_reply = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    analysis_record = relationship("Analysis")