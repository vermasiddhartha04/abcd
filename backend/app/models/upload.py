from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    filename = Column(
        String(255),
        nullable=False,
    )

    original_filename = Column(
        String(255),
        nullable=False,
    )

    file_type = Column(
        String(100),
        nullable=False,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    case_id = Column(
        Integer,
        ForeignKey("cases.id"),
        nullable=False,
    )

    # Authentication temporarily disabled
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    case = relationship(
        "Case",
    )

    user = relationship(
        "User",
    )