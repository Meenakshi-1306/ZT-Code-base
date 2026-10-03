from pydantic import BaseModel, Field


class OrganizationUpdateRequest(BaseModel):
    name: str | None = None
    registration_number: str | None = None
    industry: str | None = None
    website: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None


class OrganizationDetailsResponse(BaseModel):
    organization_id: str
    name: str
    registration_number: str | None = None
    industry: str | None = None
    website: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    verification_status: str
    members: list[str] = Field(default_factory=list)


class OrganizationDetailsAPIResponse(BaseModel):
    success: bool
    data: OrganizationDetailsResponse
    message: str


class OrganizationSettingsResponse(BaseModel):
    organization_id: str
    settings: dict = Field(default_factory=dict)
    notifications: list = Field(default_factory=list)


class OrganizationVerificationResponse(BaseModel):
    organization_id: str
    verification_status: str
    verification_type: str | None = None
    registration_number: str | None = None
    status: str | None = None
    document_status: str | None = None
    documents: list = Field(default_factory=list)