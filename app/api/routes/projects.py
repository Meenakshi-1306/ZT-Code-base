from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.database.database import get_db
from app.controllers.project_controller import ProjectController
from app.schemas.common import APIResponse

from app.schemas.project import (
    ProjectCreateRequest,
    ProjectCreateResponse,
    ProjectUpdateRequest,
    ProjectUpdateResponse,
    ProjectListResponse,
    ProjectDetailsResponse,
    ProjectMembersResponse,
    ProjectMemberAddRequest,
    ProjectMemberResponse,
    ProjectActionResponse,
    ProjectLeadUpdate,
)


router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)


# ============================================================
# PROJECT MANAGEMENT
# ============================================================


@router.get(
    "/organizations/{organization_id}/projects",
    response_model=APIResponse[ProjectListResponse],
    summary="List organization projects"
)
def list_projects(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("PROJECT_VIEW")
    )
):
    try:

        data = ProjectController.list_projects(
            db=db,
            organization_id=organization_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Projects retrieved successfully"
        }

    except ValueError as exc:

        status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# CREATE PROJECT
# ============================================================


@router.post(
    "/organizations/{organization_id}/projects",
    response_model=ProjectCreateResponse,
    summary="Create project"
)
def create_project(
    organization_id: str,
    request: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("PROJECT_CREATE")
    )
):
    try:

        project = ProjectController.create_project(
            db=db,
            organization_id=organization_id,
            request=request,
            current_user=current_user
        )

        return {
            "success": True,
            "data": {
                "project_id": project.id,
                "organization_id": project.organization_id,
                "team_id": project.team_id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "created_at": project.created_at
            },
            "message": "Project created successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "not found" in str(exc).lower():
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# PROJECT DETAILS
# ============================================================


@router.get(
    "/{project_id}",
    response_model=APIResponse[ProjectDetailsResponse],
    summary="Get project details"
)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("PROJECT_VIEW")
    )
):
    try:

        data = ProjectController.get_project(
            db=db,
            project_id=project_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Project retrieved successfully"
        }

    except ValueError as exc:

        status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# UPDATE PROJECT
# ============================================================


@router.patch(
    "/{project_id}",
    response_model=ProjectUpdateResponse,
    summary="Update project"
)
def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("PROJECT_UPDATE")
    )
):
    try:

        project = ProjectController.update_project(
            db=db,
            project_id=project_id,
            request=request,
            current_user=current_user
        )

        return {
            "success": True,
            "data": {
                "project_id": project.id,
                "organization_id": project.organization_id,
                "team_id": project.team_id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "updated_at": project.updated_at
            },
            "message": "Project updated successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "not found" in str(exc).lower():
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# DELETE PROJECT
# ============================================================


@router.delete(
    "/{project_id}",
    response_model=APIResponse[ProjectActionResponse],
    summary="Delete project"
)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("PROJECT_DELETE")
    )
):
    try:

        data = ProjectController.delete_project(
            db=db,
            project_id=project_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Project deleted successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "not found" in str(exc).lower():
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# PROJECT MEMBERS
# ============================================================


@router.get(
    "/{project_id}/members",
    response_model=APIResponse[ProjectMembersResponse],
    summary="List project members"
)
def list_project_members(
    project_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("PROJECT_VIEW")
    )
):
    try:

        data = ProjectController.list_project_members(
            db=db,
            project_id=project_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Project members retrieved successfully"
        }

    except ValueError as exc:

        status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# ADD PROJECT MEMBER
# ============================================================


@router.post(
    "/{project_id}/members",
    response_model=APIResponse[ProjectMemberResponse],
    summary="Add project member"
)
def add_project_member(
    project_id: str,
    request: ProjectMemberAddRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("PROJECT_MEMBER_MANAGE")
    )
):
    try:

        member = ProjectController.add_project_member(
            db=db,
            project_id=project_id,
            request=request,
            current_user=current_user
        )

        return {
            "success": True,
            "data": member,
            "message": "Project member added successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "not found" in str(exc).lower():
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# REMOVE PROJECT MEMBER
# ============================================================


@router.delete(
    "/{project_id}/members/{user_id}",
    response_model=APIResponse[ProjectActionResponse],
    summary="Remove project member"
)
def remove_project_member(
    project_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("PROJECT_MEMBER_MANAGE")
    )
):
    try:

        data = ProjectController.remove_project_member(
            db=db,
            project_id=project_id,
            user_id=user_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Project member removed successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "not found" in str(exc).lower():
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# PROJECT LEAD
# ============================================================


@router.patch(
    "/{project_id}/lead",
    response_model=APIResponse[ProjectActionResponse],
    summary="Assign project lead"
)
def assign_project_lead(
    project_id: str,
    request: ProjectLeadUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("PROJECT_UPDATE")
    )
):
    try:

        data = ProjectController.assign_lead(
            db=db,
            project_id=project_id,
            user_id=request.user_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Project lead assigned successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "not found" in str(exc).lower():
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )