from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.database.database import get_db
from app.controllers.team_controller import TeamController

from app.schemas.common import APIResponse

from app.schemas.team import (
    AssignTeamLeadRequest,
    AssignTeamLeadResponse,
    TeamActivityResponse,
    TeamAnomaliesResponse,
    TeamAnalyticsResponse,
    TeamDetailsResponse,
    TeamRiskResponse,
    TeamCreateRequest,
    TeamCreateResponse,
    TeamListResponse,
    TeamMemberAddRequest,
    TeamMemberActionResponse,
    TeamMembersResponse,
    TeamUpdateRequest,
    TeamUpdateResponse,
)


router = APIRouter(
    prefix="/api/teams",
    tags=["Teams"]
)


# ============================================================
# TEAM DETAILS
# ============================================================

@router.get(
    "/{team_id}",
    response_model=APIResponse[TeamDetailsResponse],
    summary="Get team details"
)
def get_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("TEAM_VIEW"))
):
    try:
        data = TeamController.get_team(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team retrieved successfully"
        }

    except ValueError as exc:
        if str(exc) == "Team not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc)
            )

        raise HTTPException(
            status_code=403,
            detail=str(exc)
        )


# ============================================================
# TEAM ACTIVITY
# ============================================================

@router.get(
    "/{team_id}/activity",
    response_model=APIResponse[TeamActivityResponse],
    summary="Get team activity"
)
def get_team_activity(
    team_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("TEAM_VIEW"))
):
    try:
        data = TeamController.get_team_activity(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team activity retrieved successfully"
        }

    except ValueError as exc:
        if str(exc) == "Team not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc)
            )

        raise HTTPException(
            status_code=403,
            detail=str(exc)
        )


# ============================================================
# TEAM ANOMALIES
# ============================================================

@router.get(
    "/{team_id}/anomalies",
    response_model=APIResponse[TeamAnomaliesResponse],
    summary="Get team anomalies"
)
def get_team_anomalies(
    team_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("ANOMALY_VIEW"))
):
    try:
        data = TeamController.get_team_anomalies(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team anomalies retrieved successfully"
        }

    except ValueError as exc:
        if str(exc) == "Team not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc)
            )

        raise HTTPException(
            status_code=403,
            detail=str(exc)
        )


# ============================================================
# TEAM RISK
# ============================================================

@router.get(
    "/{team_id}/risk",
    response_model=APIResponse[TeamRiskResponse],
    summary="Get team risk"
)
def get_team_risk(
    team_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("RISK_VIEW"))
):
    try:
        data = TeamController.get_team_risk(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team risk retrieved successfully"
        }

    except ValueError as exc:
        if str(exc) == "Team not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc)
            )

        raise HTTPException(
            status_code=403,
            detail=str(exc)
        )


# ============================================================
# TEAM ANALYTICS
# ============================================================

@router.get(
    "/{team_id}/analytics",
    response_model=APIResponse[TeamAnalyticsResponse],
    summary="Get team analytics"
)
def get_team_analytics(
    team_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("ANALYTICS_VIEW"))
):
    try:
        data = TeamController.get_team_analytics(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team analytics retrieved successfully"
        }

    except ValueError as exc:
        if str(exc) == "Team not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc)
            )

        raise HTTPException(
            status_code=403,
            detail=str(exc)
        )


# ============================================================
# ASSIGN TEAM LEAD
# ============================================================

@router.post(
    "/{team_id}/lead",
    response_model=APIResponse[AssignTeamLeadResponse],
    summary="Assign Team Lead"
)
def assign_team_lead(
    team_id: str,
    request: AssignTeamLeadRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_MEMBER_MANAGE")
    )
):
    try:
        data = TeamController.assign_team_lead(
            db=db,
            team_id=team_id,
            request=request,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team lead assigned successfully"
        }

    except ValueError as exc:
        status_code = 404 if str(exc) == "Team not found" else 400

        if (
            "access" in str(exc).lower()
            or "organization" in str(exc).lower()
            or "permission" in str(exc).lower()
        ):
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# ORGANIZATION → TEAM MANAGEMENT
# ============================================================

@router.get(
    "/organizations/{organization_id}/teams",
    response_model=APIResponse[TeamListResponse],
    summary="List organization teams"
)
def list_teams(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_VIEW")
    )
):
    try:
        data = TeamController.list_teams(
            db=db,
            organization_id=organization_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Teams retrieved successfully"
        }

    except ValueError as exc:
        status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


@router.post(
    "/organizations/{organization_id}/teams",
    response_model=APIResponse[TeamCreateResponse],
    summary="Create team"
)
def create_team(
    organization_id: str,
    request: TeamCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_CREATE")
    )
):
    try:
        team = TeamController.create_team(
            db=db,
            organization_id=organization_id,
            request=request,
            current_user=current_user
        )

        return {
            "success": True,
            "data": {
                "team_id": team.id,
                "organization_id": team.organization_id,
                "name": team.name,
                "description": team.description,
                "status": team.status,
                "lead_id": team.lead_user_id,
                "created_at": team.created_at
            },
            "message": "Team created successfully"
        }

    except ValueError as exc:
        status_code = 400

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# UPDATE TEAM
# ============================================================

@router.patch(
    "/{team_id}",
    response_model=APIResponse[TeamUpdateResponse],
    summary="Update team"
)
def update_team(
    team_id: str,
    request: TeamUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_UPDATE")
    )
):
    try:
        team = TeamController.update_team(
            db=db,
            team_id=team_id,
            request=request,
            current_user=current_user
        )

        return {
            "success": True,
            "data": {
                "team_id": team.id,
                "organization_id": team.organization_id,
                "name": team.name,
                "description": team.description,
                "status": team.status,
                "lead_id": team.lead_user_id,
                "updated_at": team.updated_at
            },
            "message": "Team updated successfully"
        }

    except ValueError as exc:
        status_code = 400

        if str(exc) == "Team not found":
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# DELETE TEAM
# ============================================================

@router.delete(
    "/{team_id}",
    summary="Delete team"
)
def delete_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_DELETE")
    )
):
    try:
        data = TeamController.delete_team(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team deleted successfully"
        }

    except ValueError as exc:
        status_code = 400

        if str(exc) == "Team not found":
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# TEAM MEMBERS
# ============================================================

@router.get(
    "/{team_id}/members",
    response_model=APIResponse[TeamMembersResponse],
    summary="List team members"
)
def list_team_members(
    team_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_VIEW")
    )
):
    try:
        data = TeamController.list_team_members(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team members retrieved successfully"
        }

    except ValueError as exc:
        status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


@router.post(
    "/{team_id}/members",
    response_model=APIResponse[TeamMemberActionResponse],
    summary="Add team member"
)
def add_team_member(
    team_id: str,
    request: TeamMemberAddRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_MEMBER_MANAGE")
    )
):
    try:
        data = TeamController.add_team_member(
            db=db,
            team_id=team_id,
            request=request,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team member added successfully"
        }

    except ValueError as exc:
        status_code = 400

        if str(exc) == "Team not found":
            status_code = 404

        if "organization" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


@router.delete(
    "/{team_id}/members/{user_id}",
    response_model=APIResponse[TeamMemberActionResponse],
    summary="Remove team member"
)
def remove_team_member(
    team_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_MEMBER_MANAGE")
    )
):
    try:
        data = TeamController.remove_team_member(
            db=db,
            team_id=team_id,
            user_id=user_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Team member removed successfully"
        }

    except ValueError as exc:
        status_code = 400

        if str(exc) == "Team not found":
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )