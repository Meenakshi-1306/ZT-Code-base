from pydantic import BaseModel, EmailStr, Field


class OrganizationRegistrationRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=200
    )

    organization_type: str | None = Field(
        default=None,
        max_length=100
    )

    registration_number: str | None = Field(
        default=None,
        max_length=100
    )

    industry: str | None = Field(
        default=None,
        max_length=100
    )

    website: str | None = Field(
        default=None,
        max_length=500
    )

    contact_email: EmailStr

    contact_phone: str | None = Field(
        default=None,
        max_length=30
    )

    address: str | None = Field(
        default=None,
        max_length=500
    )

    country: str | None = Field(
        default=None,
        max_length=100
    )

    state: str | None = Field(
        default=None,
        max_length=100
    )

    gstin: str | None = Field(
        default=None,
        max_length=50
    )


class OrganizationRegistrationResponse(BaseModel):
    organization_id: str
    organization_name: str
    email: str
    email_domain: str
    verification_status: str
    email_verified: bool
    message: str

    # Development only.
    # We will remove this before final implementation.
    development_otp: str | None = None


class OTPVerifyRequest(BaseModel):
    organization_id: str
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6
    )


class OTPVerifyResponse(BaseModel):
    organization_id: str
    email_verified: bool
    verification_status: str
    message: str


class OTPResendRequest(BaseModel):
    organization_id: str


class OTPResendResponse(BaseModel):
    organization_id: str
    message: str

    # Development only.
    development_otp: str | None = None