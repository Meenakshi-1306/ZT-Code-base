from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# PROJECT CREATE
# ============================================================

class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    team_id: str


class ProjectCreateResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str


# ============================================================
# PROJECT UPDATE
# ============================================================

class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    team_id: Optional[str] = None
    status: Optional[str] = None


class ProjectUpdateResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str


# ============================================================
# PROJECT MEMBER
# ============================================================

class ProjectMemberAddRequest(BaseModel):
    user_id: str
    role: Optional[str] = "member"


class ProjectMemberResponse(BaseModel):
    project_id: str
    user_id: str
    role: str
    status: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectMembersResponse(BaseModel):
    project_id: str
    members: List[ProjectMemberResponse]


# ============================================================
# PROJECT DETAILS
# ============================================================

class ProjectDetailsResponse(BaseModel):
    project_id: str
    organization_id: str
    team_id: str
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    members: List[ProjectMemberResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# PROJECT LIST
# ============================================================

class ProjectListItem(BaseModel):
    project_id: str
    organization_id: str
    team_id: str
    name: str
    description: Optional[str] = None
    status: str
    member_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    organization_id: str
    projects: List[ProjectListItem]
    total: int


# ============================================================
# GENERIC ACTION RESPONSE
# ============================================================

class ProjectActionResponse(BaseModel):
    success: bool
    message: str
    project_id: Optional[str] = None
    user_id: Optional[str] = None

class ProjectLeadUpdate(BaseModel):
    user_id: str