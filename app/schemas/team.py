from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, ConfigDict


# ============================================================
# TEAM CREATE
# ============================================================

class TeamCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreateResponse(BaseModel):
    team_id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    status: str
    lead_id: Optional[str] = None
    member_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TEAM UPDATE
# ============================================================

class TeamUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TeamUpdateResponse(BaseModel):
    team_id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    status: str
    lead_id: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TEAM LIST
# ============================================================

class TeamListItem(BaseModel):
    team_id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    status: str
    lead_id: Optional[str] = None
    member_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamListResponse(BaseModel):
    organization_id: str
    teams: List[TeamListItem]
    total: int


# ============================================================
# TEAM MEMBER
# ============================================================

class TeamMemberAddRequest(BaseModel):
    user_id: str


class TeamMemberResponse(BaseModel):
    user_id: str
    name: str
    email: str
    status: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamMembersResponse(BaseModel):
    team_id: str
    members: List[TeamMemberResponse]
    total: int


# ============================================================
# TEAM PROJECT
# ============================================================

class TeamProjectResponse(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TEAM DETAILS
# ============================================================

class TeamDetailsResponse(BaseModel):
    team_id: str
    organization_id: str
    name: str
    lead_id: Optional[str] = None

    members: List[str] = []

    projects: List[TeamProjectResponse] = []

    activity: List[str] = []

    anomalies: List[str] = []

    risk: Optional[Dict[str, Any]] = None

    analytics: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TEAM ACTIVITY
# ============================================================

class TeamActivityResponse(BaseModel):
    team_id: str
    activity: List[str] = []


# ============================================================
# TEAM ANOMALIES
# ============================================================

class TeamAnomaliesResponse(BaseModel):
    team_id: str
    anomalies: List[str] = []


# ============================================================
# TEAM RISK
# ============================================================

class TeamRiskResponse(BaseModel):
    team_id: str
    risk: Optional[Dict[str, Any]] = None


# ============================================================
# TEAM ANALYTICS
# ============================================================

class TeamAnalyticsResponse(BaseModel):
    team_id: str
    analytics: Dict[str, Any] = {}


# ============================================================
# TEAM LEAD
# ============================================================

class AssignTeamLeadRequest(BaseModel):
    user_id: str


class AssignTeamLeadResponse(BaseModel):
    team_id: str
    lead_id: Optional[str] = None


# ============================================================
# TEAM ACTION
# ============================================================

class TeamActionResponse(BaseModel):
    success: bool
    message: str
    team_id: Optional[str] = None
    user_id: Optional[str] = None
# ============================================================
# TEAM MEMBER ACTION
# ============================================================

class TeamMemberActionResponse(BaseModel):
    success: bool
    message: str
    team_id: Optional[str] = None
    user_id: Optional[str] = None