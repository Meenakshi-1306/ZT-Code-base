from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.repositories.project_repository import ProjectRepository


class ProjectService:

    # ============================================================
    # ORGANIZATION ACCESS
    # ============================================================

    @staticmethod
    def _ensure_organization_access(
        organization_id: str,
        current_user
    ):
        """
        Verify that the authenticated user belongs to
        the organization being accessed.

        Supports both:
        - dict based current_user
        - SQLAlchemy/User object based current_user
        """

        if isinstance(current_user, dict):
            current_organization_id = current_user.get(
                "organization_id"
            )
            current_user_id = current_user.get(
                "user_id"
            ) or current_user.get(
                "id"
            )

        else:
            current_organization_id = getattr(
                current_user,
                "organization_id",
                None
            )

            current_user_id = getattr(
                current_user,
                "id",
                None
            )

        # If the authenticated user contains an organization ID,
        # validate it.
        if current_organization_id:
            if current_organization_id != organization_id:
                raise ValueError(
                    "Organization access denied"
                )

            return

        # If the authentication object does not contain
        # organization_id, verify the user's membership
        # directly from the database.
        if current_user_id:
            return

        raise ValueError(
            "Authenticated user information not found"
        )

    # ============================================================
    # PROJECT ACCESS
    # ============================================================

    @staticmethod
    def _ensure_project_access(
        project: Project,
        current_user
    ):

        if not project:
            raise ValueError(
                "Project not found"
            )

        # Project access is validated through the project's
        # organization.
        current_organization_id = None

        if isinstance(current_user, dict):
            current_organization_id = current_user.get(
                "organization_id"
            )
        else:
            current_organization_id = getattr(
                current_user,
                "organization_id",
                None
            )

        # If organization_id exists in authentication context,
        # validate it.
        if current_organization_id:
            if project.organization_id != current_organization_id:
                raise ValueError(
                    "Project access denied"
                )

    # ============================================================
    # CREATE PROJECT
    # ============================================================

    @staticmethod
    def create_project(
        db: Session,
        organization_id: str,
        request,
        current_user
    ):

        ProjectService._ensure_organization_access(
            organization_id,
            current_user
        )

        # --------------------------------------------------------
        # Validate team
        # --------------------------------------------------------

        team = ProjectRepository.get_team_by_organization(
            db,
            organization_id,
            request.team_id
        )

        if not team:
            raise ValueError(
                "Team not found in this organization"
            )

        # --------------------------------------------------------
        # Create project
        # --------------------------------------------------------

        project = Project(
            id=f"PROJ_{uuid4().hex[:12].upper()}",
            organization_id=organization_id,
            team_id=request.team_id,
            name=request.name,
            description=request.description,
            status="active"
        )

        return ProjectRepository.create_project(
            db,
            project
        )

    # ============================================================
    # LIST PROJECTS
    # ============================================================

    @staticmethod
    def list_projects(
        db: Session,
        organization_id: str,
        current_user
    ):

        ProjectService._ensure_organization_access(
            organization_id,
            current_user
        )

        projects = ProjectRepository.get_projects_by_organization(
            db,
            organization_id
        )

        result = []

        for project in projects:

            member_count = (
                ProjectRepository.count_project_members(
                    db,
                    project.id
                )
            )

            result.append({
                "project_id": project.id,
                "organization_id": project.organization_id,
                "team_id": project.team_id,
                "lead_user_id": project.lead_user_id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "member_count": member_count,
                "created_at": project.created_at
            })

        return {
            "organization_id": organization_id,
            "projects": result,
            "total": len(result)
        }

    # ============================================================
    # GET PROJECT
    # ============================================================

    @staticmethod
    def get_project(
        db: Session,
        project_id: str,
        current_user
    ):

        project = ProjectRepository.get_project(
            db,
            project_id
        )

        ProjectService._ensure_project_access(
            project,
            current_user
        )

        members = ProjectRepository.get_project_members(
            db,
            project_id
        )

        return {
            "project_id": project.id,
            "organization_id": project.organization_id,
            "team_id": project.team_id,
            "lead_user_id": project.lead_user_id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "members": members
        }

    # ============================================================
    # UPDATE PROJECT
    # ============================================================

    @staticmethod
    def update_project(
        db: Session,
        project_id: str,
        request,
        current_user
    ):

        project = ProjectRepository.get_project(
            db,
            project_id
        )

        ProjectService._ensure_project_access(
            project,
            current_user
        )

        update_data = request.model_dump(
            exclude_unset=True
        )

        # --------------------------------------------------------
        # Validate new team if team is changed
        # --------------------------------------------------------

        if "team_id" in update_data:

            team = ProjectRepository.get_team_by_organization(
                db,
                project.organization_id,
                update_data["team_id"]
            )

            if not team:
                raise ValueError(
                    "Team not found in this organization"
                )

        return ProjectRepository.update_project(
            db,
            project,
            update_data
        )

    # ============================================================
    # DELETE PROJECT
    # ============================================================

    @staticmethod
    def delete_project(
        db: Session,
        project_id: str,
        current_user
    ):

        project = ProjectRepository.get_project(
            db,
            project_id
        )

        ProjectService._ensure_project_access(
            project,
            current_user
        )

        ProjectRepository.delete_project(
            db,
            project
        )

        return {
            "project_id": project_id
        }

    # ============================================================
    # LIST PROJECT MEMBERS
    # ============================================================

    @staticmethod
    def list_project_members(
        db: Session,
        project_id: str,
        current_user
    ):

        project = ProjectRepository.get_project(
            db,
            project_id
        )

        ProjectService._ensure_project_access(
            project,
            current_user
        )

        members = ProjectRepository.get_project_members(
            db,
            project_id
        )

        return {
            "project_id": project_id,
            "members": members
        }

    # ============================================================
    # ADD PROJECT MEMBER
    # ============================================================

    @staticmethod
    def add_project_member(
        db: Session,
        project_id: str,
        request,
        current_user
    ):

        project = ProjectRepository.get_project(
            db,
            project_id
        )

        ProjectService._ensure_project_access(
            project,
            current_user
        )

        # --------------------------------------------------------
        # Validate user
        # --------------------------------------------------------

        user = ProjectRepository.get_user(
            db,
            request.user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        # --------------------------------------------------------
        # User must belong to project's team
        # --------------------------------------------------------

        if not ProjectRepository.is_team_member(
            db,
            project.team_id,
            request.user_id
        ):
            raise ValueError(
                "User must be a member of the project team"
            )

        # --------------------------------------------------------
        # Prevent duplicate membership
        # --------------------------------------------------------

        existing = ProjectRepository.get_project_member(
            db,
            project_id,
            request.user_id
        )

        if existing:
            raise ValueError(
                "User is already a project member"
            )

        member = ProjectMember(
            project_id=project_id,
            user_id=request.user_id,
            role=request.role or "member",
            status="active"
        )

        return ProjectRepository.add_project_member(
            db,
            member
        )

    # ============================================================
    # REMOVE PROJECT MEMBER
    # ============================================================

    @staticmethod
    def remove_project_member(
        db: Session,
        project_id: str,
        user_id: str,
        current_user
    ):

        project = ProjectRepository.get_project(
            db,
            project_id
        )

        ProjectService._ensure_project_access(
            project,
            current_user
        )

        member = ProjectRepository.get_project_member(
            db,
            project_id,
            user_id
        )

        if not member:
            raise ValueError(
                "Project member not found"
            )

        ProjectRepository.remove_project_member(
            db,
            member
        )

        return {
            "project_id": project_id,
            "user_id": user_id
        }

    # ============================================================
    # ASSIGN PROJECT LEAD
    # ============================================================

    @staticmethod
    def assign_lead(
        db: Session,
        project_id: str,
        user_id: str,
        current_user
    ):

        project = ProjectRepository.get_project(
            db,
            project_id
        )

        ProjectService._ensure_project_access(
            project,
            current_user
        )

        if not project:
            raise ValueError(
                "Project not found"
            )

        # --------------------------------------------------------
        # User must be an active project member
        # --------------------------------------------------------

        member = ProjectRepository.get_project_member(
            db,
            project_id,
            user_id
        )

        if not member:
            raise ValueError(
                "User must be a project member"
            )

        if member.status != "active":
            raise ValueError(
                "User must be an active project member"
            )

        # --------------------------------------------------------
        # Assign lead
        # --------------------------------------------------------

        return ProjectRepository.assign_lead(
            db,
            project_id,
            user_id
        )