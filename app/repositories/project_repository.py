from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.user import User


class ProjectRepository:

    # ============================================================
    # PROJECT
    # ============================================================

    @staticmethod
    def get_project(
        db: Session,
        project_id: str
    ):
        return (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

    @staticmethod
    def get_project_by_organization(
        db: Session,
        organization_id: str,
        project_id: str
    ):
        return (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.organization_id == organization_id
            )
            .first()
        )

    @staticmethod
    def get_projects_by_organization(
        db: Session,
        organization_id: str
    ):
        return (
            db.query(Project)
            .filter(
                Project.organization_id == organization_id
            )
            .order_by(Project.created_at.desc())
            .all()
        )

    @staticmethod
    def create_project(
        db: Session,
        project: Project
    ):
        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def update_project(
        db: Session,
        project: Project,
        update_data: dict
    ):
        for key, value in update_data.items():
            if value is not None:
                setattr(project, key, value)

        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def delete_project(
        db: Session,
        project: Project
    ):
        db.delete(project)
        db.commit()

    # ============================================================
    # TEAM
    # ============================================================

    @staticmethod
    def get_team(
        db: Session,
        team_id: str
    ):
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
    ):
        return (
            db.query(Team)
            .filter(
                Team.id == team_id,
                Team.organization_id == organization_id
            )
            .first()
        )

    # ============================================================
    # USERS
    # ============================================================

    @staticmethod
    def get_user(
        db: Session,
        user_id: str
    ):
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    # ============================================================
    # TEAM MEMBERS
    # ============================================================

    @staticmethod
    def is_team_member(
        db: Session,
        team_id: str,
        user_id: str
    ):
        return (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id
            )
            .first()
            is not None
        )

    # ============================================================
    # PROJECT MEMBERS
    # ============================================================

    @staticmethod
    def get_project_members(
        db: Session,
        project_id: str
    ):
        return (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id
            )
            .order_by(ProjectMember.joined_at.asc())
            .all()
        )

    @staticmethod
    def get_project_member(
        db: Session,
        project_id: str,
        user_id: str
    ):
        return (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def add_project_member(
        db: Session,
        member: ProjectMember
    ):
        db.add(member)
        db.commit()
        db.refresh(member)

        return member

    @staticmethod
    def remove_project_member(
        db: Session,
        member: ProjectMember
    ):
        db.delete(member)
        db.commit()

    @staticmethod
    def count_project_members(
        db: Session,
        project_id: str
    ):
        return (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id
            )
            .count()
        )

    # ============================================================
    # PROJECT LEAD
    # ============================================================

    @staticmethod
    def assign_lead(
        db: Session,
        project_id: str,
        user_id: str
    ):
        project = (
            db.query(Project)
            .filter(
                Project.id == project_id
            )
            .first()
        )

        if not project:
            return None

        project.lead_user_id = user_id

        db.commit()
        db.refresh(project)

        return project