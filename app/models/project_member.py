from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id = Column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role = Column(
        String,
        nullable=False,
        default="member",
    )

    status = Column(
        String,
        nullable=False,
        default="active",
    )

    joined_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships

    project = relationship(
        "Project",
        back_populates="members",
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        backref="project_memberships",
    )