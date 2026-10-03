from sqlalchemy.orm import Session

from app.services.project_service import ProjectService
from fastapi import HTTPException

class ProjectController:

    # ============================================================
    # PROJECT
    # ============================================================

    @staticmethod
    def create_project(
        db: Session,
        organization_id: str,
        request,
        current_user
    ):

        return ProjectService.create_project(
            db=db,
            organization_id=organization_id,
            request=request,
            current_user=current_user
        )

    @staticmethod
    def list_projects(
        db: Session,
        organization_id: str,
        current_user
    ):

        return ProjectService.list_projects(
            db=db,
            organization_id=organization_id,
            current_user=current_user
        )

    @staticmethod
    def get_project(
        db: Session,
        project_id: str,
        current_user
    ):

        return ProjectService.get_project(
            db=db,
            project_id=project_id,
            current_user=current_user
        )

    @staticmethod
    def update_project(
        db: Session,
        project_id: str,
        request,
        current_user
    ):

        return ProjectService.update_project(
            db=db,
            project_id=project_id,
            request=request,
            current_user=current_user
        )

    @staticmethod
    def delete_project(
        db: Session,
        project_id: str,
        current_user
    ):

        return ProjectService.delete_project(
            db=db,
            project_id=project_id,
            current_user=current_user
        )

    # ============================================================
    # PROJECT MEMBERS
    # ============================================================

    @staticmethod
    def list_project_members(
        db: Session,
        project_id: str,
        current_user
    ):

        return ProjectService.list_project_members(
            db=db,
            project_id=project_id,
            current_user=current_user
        )

    @staticmethod
    def add_project_member(
        db: Session,
        project_id: str,
        request,
        current_user
    ):

        return ProjectService.add_project_member(
            db=db,
            project_id=project_id,
            request=request,
            current_user=current_user
        )

    @staticmethod
    def remove_project_member(
        db: Session,
        project_id: str,
        user_id: str,
        current_user
    ):

        return ProjectService.remove_project_member(
            db=db,
            project_id=project_id,
            user_id=user_id,
            current_user=current_user
        )
    @staticmethod
    def assign_lead(
    db: Session,
    project_id: str,
    user_id: str,
):
        try:
            return ProjectService.assign_lead(
            db,
            project_id,
            user_id,
        )
        except ValueError as e:
            raise HTTPException(
            status_code=400,
            detail=str(e),
        )