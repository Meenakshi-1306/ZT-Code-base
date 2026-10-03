from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database.base import Base


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    role_id: Mapped[str | None] = mapped_column(
        ForeignKey("roles.id"),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String,
        default="active",
        nullable=False
    )

    joined_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    organization = relationship(
        "Organization",
        back_populates="members"
    )

    user = relationship(
        "User",
        back_populates="organization_members"
    )

    role = relationship(
        "Role",
        back_populates="organization_members"
    )