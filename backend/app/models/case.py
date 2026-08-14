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


class Case(Base):
    __tablename__ = "cases"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_no = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    gstin = Column(
        String(20),
        nullable=False,
        index=True,
    )

    taxpayer_name = Column(
        String(255),
        nullable=False,
    )

    notice_type = Column(
        String(100),
        nullable=False,
    )

    financial_year = Column(
        String(20),
        nullable=False,
    )

    status = Column(
        String(50),
        default="Pending",
        nullable=False,
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    owner = relationship(
        "User",
        back_populates="cases",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )