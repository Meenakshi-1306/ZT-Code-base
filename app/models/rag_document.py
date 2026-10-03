from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey

from app.database.base import Base


class RagDocument(Base):

    __tablename__ = "rag_documents"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    organization_id = Column(
        String,
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    filename = Column(
        String,
        nullable=False,
    )

    original_filename = Column(
        String,
        nullable=False,
    )

    standard = Column(
        String,
        nullable=True,
    )

    version = Column(
        String,
        nullable=True,
    )

    pages = Column(
        Integer,
        default=0,
        nullable=False,
    )

    chunks = Column(
        Integer,
        default=0,
        nullable=False,
    )

    file_path = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        default="indexed",
        nullable=False,
    )

    uploaded_by = Column(
        String,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )