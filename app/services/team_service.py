from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember

from app.repositories.team_repository import TeamRepository
from app.repositories.organization_repository import OrganizationRepository


class TeamService:

    # ============================================================
    # EXISTING ACCESS HELPERS
    # ============================================================

    @staticmethod
    def _get_current_organization_id(
        current_user: User | None
    ) -> str | None:

        if not current_user:
            return None

        org_id = getattr(
            current_user,
            "current_organization_id",
            None
        )

        if org_id:
            return org_id

        if current_user.organization_members:

            return current_user.organization_members[
                0
            ].organization_id

        return None

    @staticmethod
    def _ensure_team_access(
        team,
        current_user: User
    ) -> None:

        if not team:
            raise ValueError("Team not found")

        organization_id = (
            TeamService._get_current_organization_id(
                current_user
            )
        )

        if team.organization_id != organization_id:

            raise ValueError(
                "User does not have access to this team"
            )

    # ============================================================
    # LIST TEAMS
    # ============================================================

    @staticmethod
    def list_teams(
        db: Session,
        organization_id: str,
        current_user: User
    ):

        current_org_id = (
            TeamService._get_current_organization_id(
                current_user
            )
        )

        if current_org_id != organization_id:
            raise ValueError(
                "User does not have access to this organization"
            )

        organization = OrganizationRepository.get_organization(
            db,
            organization_id
        )

        if not organization:
            raise ValueError(
                "Organization not found"
            )

        teams = TeamRepository.get_teams_by_organization(
            db,
            organization_id
        )

        result = []

        for team in teams:

            members = TeamRepository.get_team_members(
                db,
                team.id
            )

            result.append({
                "team_id": team.id,
                "organization_id": team.organization_id,
                "name": team.name,
                "description": team.description,
                "status": team.status,
                "lead_id": team.lead_user_id,
                "member_count": len(members),
                "created_at": team.created_at,
                "updated_at": team.updated_at
            })

        return {
            "organization_id": organization_id,
            "teams": result,
            "total": len(result)
        }

    # ============================================================
    # CREATE TEAM
    # ============================================================

    @staticmethod
    def create_team(
        db: Session,
        organization_id: str,
        name: str,
        description: str | None,
        current_user: User
    ):

        current_org_id = (
            TeamService._get_current_organization_id(
                current_user
            )
        )

        if current_org_id != organization_id:

            raise ValueError(
                "User does not have access to this organization"
            )

        organization = OrganizationRepository.get_organization(
            db,
            organization_id
        )

        if not organization:

            raise ValueError(
                "Organization not found"
            )

        existing_team = TeamRepository.get_team_by_name(
            db,
            organization_id,
            name.strip()
        )

        if existing_team:

            raise ValueError(
                "A team with this name already exists"
            )

        team = Team(
            id=f"TEAM_{uuid4().hex[:10].upper()}",
            organization_id=organization_id,
            name=name.strip(),
            description=description,
            status="active",
            lead_user_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        return TeamRepository.create_team(
            db,
            team
        )

    # ============================================================
    # GET TEAM
    # ============================================================

    @staticmethod
    def get_team(
        db: Session,
        team_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        # --------------------------------------------------------
        # MEMBERS
        # --------------------------------------------------------

        members = TeamRepository.get_team_members(
            db,
            team.id
        )

        # --------------------------------------------------------
        # PROJECTS
        # --------------------------------------------------------

        projects = TeamRepository.get_team_projects(
            db,
            team.id
        )

        project_data = []

        for project in projects:

            project_data.append({
                "project_id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "created_at": project.created_at
            })

        # --------------------------------------------------------
        # RESPONSE
        # --------------------------------------------------------

        return {
            "team_id": team.id,
            "organization_id": team.organization_id,
            "name": team.name,
            "lead_id": team.lead_user_id,
            "members": members,
            "projects": project_data,
            "activity": [],
            "anomalies": [],
            "risk": None,
            "analytics": {},
        }
    # ============================================================
    # UPDATE TEAM
    # ============================================================

    @staticmethod
    def update_team(
        db: Session,
        team_id: str,
        update_data: dict,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        if "name" in update_data:

            existing_team = (
                TeamRepository.get_team_by_name(
                    db,
                    team.organization_id,
                    update_data["name"]
                )
            )

            if (
                existing_team
                and existing_team.id != team.id
            ):

                raise ValueError(
                    "A team with this name already exists"
                )

        update_data["updated_at"] = datetime.utcnow()

        return TeamRepository.update_team(
            db,
            team,
            update_data
        )

    # ============================================================
    # DELETE TEAM
    # ============================================================

    @staticmethod
    def delete_team(
        db: Session,
        team_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        TeamRepository.delete_team(
            db,
            team
        )

        return {
            "success": True,
            "message": "Team deleted successfully"
        }

    # ============================================================
    # LIST TEAM MEMBERS
    # ============================================================

    @staticmethod
    def list_team_members(
        db: Session,
        team_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        records = TeamRepository.get_team_member_records(
            db,
            team_id
        )

        members = []

        for record in records:

            user = TeamRepository.get_user(
                db,
                record.user_id
            )

            if not user:
                continue

            members.append({
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "status": record.status,
                "joined_at": record.joined_at
            })

        return {
            "team_id": team_id,
            "members": members,
            "total": len(members)
        }

    # ============================================================
    # ADD TEAM MEMBER
    # ============================================================

    @staticmethod
    def add_team_member(
        db: Session,
        team_id: str,
        user_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        user = TeamRepository.get_user(
            db,
            user_id
        )

        if not user:

            raise ValueError(
                "User not found"
            )

        # Make sure user belongs to same organization

        user_belongs_to_org = any(
            membership.organization_id
            == team.organization_id
            for membership
            in user.organization_members
        )

        if not user_belongs_to_org:

            raise ValueError(
                "User does not belong to the team's organization"
            )

        existing_member = (
            TeamRepository.get_team_member(
                db,
                team_id,
                user_id
            )
        )

        if existing_member:

            if existing_member.status == "active":

                raise ValueError(
                    "User is already a member of this team"
                )

            existing_member = (
                TeamRepository.update_team_member(
                    db,
                    existing_member,
                    {
                        "status": "active",
                        "joined_at": datetime.utcnow()
                    }
                )
            )

            return {
                "team_id": team_id,
                "user_id": user_id,
                "message": "User added to team successfully"
            }

        team_member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            status="active",
            joined_at=datetime.utcnow()
        )

        TeamRepository.add_team_member(
            db,
            team_member
        )

        return {
            "team_id": team_id,
            "user_id": user_id,
            "message": "User added to team successfully"
        }

    # ============================================================
    # REMOVE TEAM MEMBER
    # ============================================================

    @staticmethod
    def remove_team_member(
        db: Session,
        team_id: str,
        user_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        member = TeamRepository.get_team_member(
            db,
            team_id,
            user_id
        )

        if not member:

            raise ValueError(
                "User is not a member of this team"
            )

        # Don't leave a deleted team lead reference

        if team.lead_user_id == user_id:

            team.lead_user_id = None

            db.commit()

        TeamRepository.remove_team_member(
            db,
            member
        )

        return {
            "team_id": team_id,
            "user_id": user_id,
            "message": "User removed from team successfully"
        }

    # ============================================================
    # EXISTING ACTIVITY
    # ============================================================

    @staticmethod
    def get_team_activity(
        db: Session,
        team_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        return {
            "team_id": team.id,
            "activity": []
        }

    # ============================================================
    # EXISTING ANOMALIES
    # ============================================================

    @staticmethod
    def get_team_anomalies(
        db: Session,
        team_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        return {
            "team_id": team.id,
            "anomalies": []
        }

    # ============================================================
    # EXISTING RISK
    # ============================================================

    @staticmethod
    def get_team_risk(
        db: Session,
        team_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        return {
            "team_id": team.id,
            "risk": None
        }

    # ============================================================
    # EXISTING ANALYTICS
    # ============================================================

    @staticmethod
    def get_team_analytics(
        db: Session,
        team_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        TeamService._ensure_team_access(
            team,
            current_user
        )

        return {
            "team_id": team.id,
            "analytics": {}
        }

    # ============================================================
    # TEAM LEAD
    # ============================================================

    @staticmethod
    def assign_team_lead(
        db: Session,
        team_id: str,
        user_id: str,
        current_user: User
    ):

        team = TeamRepository.get_team(
            db,
            team_id
        )

        if not team:
            raise ValueError(
                "Team not found"
            )

        organization_id = (
            TeamService._get_current_organization_id(
                current_user
            )
        )

        if team.organization_id != organization_id:

            raise ValueError(
                "User does not have access to this team"
            )

        user = TeamRepository.get_user(
            db,
            user_id
        )

        if not user:

            raise ValueError(
                "User not found"
            )

        user_belongs_to_team_org = any(
            membership.organization_id
            == team.organization_id
            for membership
            in user.organization_members
        )

        if not user_belongs_to_team_org:

            raise ValueError(
                "User does not belong to the team's organization"
            )

        is_member = TeamRepository.is_team_member(
            db,
            team_id,
            user_id
        )

        if not is_member:

            raise ValueError(
                "User must be a team member before becoming team lead"
            )

        team = TeamRepository.assign_team_lead(
            db,
            team,
            user_id
        )

        return {
            "team_id": team.id,
            "lead_id": team.lead_user_id
        }