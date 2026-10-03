from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EmailOTP(Base):
    __tablename__ = "email_otps"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    organization_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("organizations.id"),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    otp_hash: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    max_attempts: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False
    )

    resend_available_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    organization = relationship(
        "Organization",
        back_populates="email_otps"
    )