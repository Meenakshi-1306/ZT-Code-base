from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================
# ROLE
# ============================================================

class RoleCreateRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )


class RoleUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )


class PermissionResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    module: str


class RoleResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: str | None = None
    is_system_role: bool
    created_at: datetime
    updated_at: datetime
    permissions: list[PermissionResponse] = []


class RoleListResponse(BaseModel):
    organization_id: str
    roles: list[RoleResponse]
    total: int


# ============================================================
# PERMISSION
# ============================================================

class PermissionListResponse(BaseModel):
    permissions: list[PermissionResponse]
    total: int


# ============================================================
# ROLE → PERMISSION
# ============================================================

class RolePermissionRequest(BaseModel):
    permission_ids: list[str]


class RolePermissionResponse(BaseModel):
    role_id: str
    permission_ids: list[str]
    message: str