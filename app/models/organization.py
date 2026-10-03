from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    organization_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    registration_number: Mapped[str | None] = mapped_column(
        String,
        unique=True,
        nullable=True
    )

    industry: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    website: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    contact_email: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    email_domain: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    contact_phone: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    country: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    state: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    gstin: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    verification_status: Mapped[str] = mapped_column(
        String,
        default="pending",
        nullable=False
    )

    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Organization members
    members = relationship(
        "OrganizationMember",
        back_populates="organization"
    )

    # Organization teams
    teams = relationship(
        "Team",
        back_populates="organization"
    )

    # Organization verification records
    verifications = relationship(
        "OrganizationVerification",
        back_populates="organization",
        cascade="all, delete-orphan"
    )

    # Email OTP records
    email_otps = relationship(
        "EmailOTP",
        back_populates="organization",
        cascade="all, delete-orphan"
    )

    # Verification documents
    verification_documents = relationship(
        "VerificationDocument",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    data_sources = relationship(
    "DataSource",
    back_populates="organization",
    cascade="all, delete-orphan"
)