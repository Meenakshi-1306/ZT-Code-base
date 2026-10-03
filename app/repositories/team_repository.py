from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.user import User
from app.models.project import Project

class TeamRepository:

    # ============================================================
    # TEAM
    # ============================================================

    @staticmethod
    def get_team(
        db: Session,
        team_id: str
    ) -> Team | None:

        return (
            db.query(Team)
            .filter(Team.id == team_id)
            .first()
        )

    @staticmethod
    def get_team_by_organization(
        db: Session,
        organization_id: str,
        team_id: str
    ) -> Team | None:

        return (
            db.query(Team)
            .filter(
                Team.organization_id == organization_id,
                Team.id == team_id
            )
            .first()
        )

    @staticmethod
    def get_teams_by_organization(
        db: Session,
        organization_id: str
    ) -> list[Team]:

        return (
            db.query(Team)
            .filter(
                Team.organization_id == organization_id
            )
            .order_by(Team.name.asc())
            .all()
        )

    @staticmethod
    def get_team_by_name(
        db: Session,
        organization_id: str,
        name: str
    ) -> Team | None:

        return (
            db.query(Team)
            .filter(
                Team.organization_id == organization_id,
                Team.name == name
            )
            .first()
        )

    @staticmethod
    def create_team(
        db: Session,
        team: Team
    ) -> Team:

        db.add(team)
        db.commit()
        db.refresh(team)

        return team

    @staticmethod
    def update_team(
        db: Session,
        team: Team,
        update_data: dict
    ) -> Team:

        for field, value in update_data.items():

            if hasattr(team, field):
                setattr(team, field, value)

        db.commit()
        db.refresh(team)

        return team

    @staticmethod
    def delete_team(
        db: Session,
        team: Team
    ):

        db.delete(team)
        db.commit()

    # ============================================================
    # MEMBERS
    # ============================================================

    @staticmethod
    def get_team_members(
        db: Session,
        team_id: str
    ) -> list[str]:

        members = (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.status == "active"
            )
            .all()
        )

        return [
            member.user_id
            for member in members
        ]

    @staticmethod
    def get_team_member_records(
        db: Session,
        team_id: str
    ) -> list[TeamMember]:

        return (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id
            )
            .order_by(
                TeamMember.joined_at.asc()
            )
            .all()
        )

    @staticmethod
    def get_team_member(
        db: Session,
        team_id: str,
        user_id: str
    ) -> TeamMember | None:

        return (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def add_team_member(
        db: Session,
        team_member: TeamMember
    ) -> TeamMember:

        db.add(team_member)
        db.commit()
        db.refresh(team_member)

        return team_member

    @staticmethod
    def update_team_member(
        db: Session,
        team_member: TeamMember,
        update_data: dict
    ) -> TeamMember:

        for field, value in update_data.items():

            if hasattr(team_member, field):
                setattr(
                    team_member,
                    field,
                    value
                )

        db.commit()
        db.refresh(team_member)

        return team_member

    @staticmethod
    def remove_team_member(
        db: Session,
        team_member: TeamMember
    ):

        db.delete(team_member)
        db.commit()

    # ============================================================
    # USERS
    # ============================================================

    @staticmethod
    def get_user(
        db: Session,
        user_id: str
    ) -> User | None:

        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def is_team_member(
        db: Session,
        team_id: str,
        user_id: str
    ) -> bool:

        member = (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.status == "active"
            )
            .first()
        )

        return member is not None

    # ============================================================
    # TEAM LEAD
    # ============================================================

    @staticmethod
    def assign_team_lead(
        db: Session,
        team: Team,
        user_id: str
    ) -> Team:

        team.lead_user_id = user_id

        db.commit()
        db.refresh(team)

        return team
        # ============================================================
    # PROJECTS
    # ============================================================

    @staticmethod
    def get_team_projects(
        db: Session,
        team_id: str
    ) -> list[Project]:

        return (
            db.query(Project)
            .filter(
                Project.team_id == team_id
            )
            .order_by(
                Project.created_at.desc()
            )
            .all()
        )