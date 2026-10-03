from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# ADD USER
# ============================================================

class UserCreateRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    email: EmailStr

    role_id: str | None = None


# ============================================================
# UPDATE USER
# ============================================================

class UserUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    email: EmailStr | None = None

    role_id: str | None = None


# ============================================================
# UPDATE USER STATUS
# ============================================================

class UserStatusUpdateRequest(BaseModel):
    status: str = Field(
        ...,
        pattern="^(active|inactive|suspended)$",
    )


# ============================================================
# ROLE SUMMARY
# ============================================================

class UserRoleResponse(BaseModel):
    role_id: str | None = None
    name: str | None = None


# ============================================================
# TEAM SUMMARY
# ============================================================

class UserTeamResponse(BaseModel):
    team_id: str
    name: str


# ============================================================
# USER LIST ITEM
# ============================================================

class UserListItemResponse(BaseModel):

    user_id: str

    name: str

    email: str

    role_id: str | None = None

    role_name: str | None = None

    status: str

    team_ids: list[str] = []


# ============================================================
# USER LIST RESPONSE
# ============================================================

class UserListResponse(BaseModel):

    organization_id: str

    users: list[UserListItemResponse]

    total: int

    page: int

    page_size: int


# ============================================================
# USER DETAILS
# ============================================================

class UserDetailsResponse(BaseModel):

    user_id: str

    name: str

    email: str

    status: str

    email_verified: bool

    account_mode: str

    role: UserRoleResponse | None = None

    teams: list[UserTeamResponse] = []

    projects: list = []

    created_at: datetime | None = None

    updated_at: datetime | None = None


# ============================================================
# ADD USER RESPONSE
# ============================================================

class UserCreateResponse(BaseModel):

    success: bool

    user_id: str

    organization_id: str

    status: str

    role_id: str | None = None

    message: str


# ============================================================
# STATUS RESPONSE
# ============================================================

class UserStatusResponse(BaseModel):

    success: bool

    user_id: str

    organization_id: str

    status: str

    message: str
class UserRoleUpdateRequest(BaseModel):
    role_id: str


class UserRoleUpdateResponse(BaseModel):
    user_id: str
    organization_id: str
    role_id: str
    role_name: str