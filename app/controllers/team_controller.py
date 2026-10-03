from sqlalchemy.orm import Session

from app.models.user import User

from app.schemas.team import (
    AssignTeamLeadRequest,
    TeamCreateRequest,
    TeamMemberAddRequest,
    TeamUpdateRequest
)

from app.services.team_service import TeamService


class TeamController:

    # ============================================================
    # TEAM MANAGEMENT
    # ============================================================

    @staticmethod
    def list_teams(
        db: Session,
        organization_id: str,
        current_user: User
    ):
        return TeamService.list_teams(
            db=db,
            organization_id=organization_id,
            current_user=current_user
        )

    @staticmethod
    def create_team(
        db: Session,
        organization_id: str,
        request: TeamCreateRequest,
        current_user: User
    ):
        return TeamService.create_team(
            db=db,
            organization_id=organization_id,
            name=request.name,
            description=request.description,
            current_user=current_user
        )

    @staticmethod
    def update_team(
        db: Session,
        team_id: str,
        request: TeamUpdateRequest,
        current_user: User
    ):
        return TeamService.update_team(
            db=db,
            team_id=team_id,
            update_data=request.model_dump(
                exclude_unset=True
            ),
            current_user=current_user
        )

    @staticmethod
    def delete_team(
        db: Session,
        team_id: str,
        current_user: User
    ):
        return TeamService.delete_team(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

    # ============================================================
    # MEMBERS
    # ============================================================

    @staticmethod
    def list_team_members(
        db: Session,
        team_id: str,
        current_user: User
    ):
        return TeamService.list_team_members(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

    @staticmethod
    def add_team_member(
        db: Session,
        team_id: str,
        request: TeamMemberAddRequest,
        current_user: User
    ):
        return TeamService.add_team_member(
            db=db,
            team_id=team_id,
            user_id=request.user_id,
            current_user=current_user
        )

    @staticmethod
    def remove_team_member(
        db: Session,
        team_id: str,
        user_id: str,
        current_user: User
    ):
        return TeamService.remove_team_member(
            db=db,
            team_id=team_id,
            user_id=user_id,
            current_user=current_user
        )

    # ============================================================
    # EXISTING TEAM APIs
    # ============================================================

    @staticmethod
    def get_team(
        db: Session,
        team_id: str,
        current_user: User
    ):
        return TeamService.get_team(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

    @staticmethod
    def get_team_activity(
        db: Session,
        team_id: str,
        current_user: User
    ):
        return TeamService.get_team_activity(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

    @staticmethod
    def get_team_anomalies(
        db: Session,
        team_id: str,
        current_user: User
    ):
        return TeamService.get_team_anomalies(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

    @staticmethod
    def get_team_risk(
        db: Session,
        team_id: str,
        current_user: User
    ):
        return TeamService.get_team_risk(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

    @staticmethod
    def get_team_analytics(
        db: Session,
        team_id: str,
        current_user: User
    ):
        return TeamService.get_team_analytics(
            db=db,
            team_id=team_id,
            current_user=current_user
        )

    @staticmethod
    def assign_team_lead(
        db: Session,
        team_id: str,
        request: AssignTeamLeadRequest,
        current_user: User
    ):
        return TeamService.assign_team_lead(
            db=db,
            team_id=team_id,
            user_id=request.user_id,
            current_user=current_user
        )