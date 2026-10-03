from datetime import datetime

from pydantic import BaseModel, Field


class OrganizationVerificationRequest(BaseModel):
    verification_type: str = Field(
        default="ORGANIZATION",
        max_length=100,
    )

    registration_number: str | None = Field(
        default=None,
        max_length=100,
    )


class OrganizationVerificationResponse(BaseModel):
    organization_id: str
    verification_id: str | None = None
    status: str
    submitted_at: datetime | None = None
    updated_at: datetime | None = None