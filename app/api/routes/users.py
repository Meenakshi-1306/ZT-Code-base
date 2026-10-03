from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.database.database import get_db

from app.controllers.user_controller import UserController

from app.schemas.user import (
    UserCreateRequest,
    UserCreateResponse,
    UserDetailsResponse,
    UserListResponse,
    UserStatusResponse,
    UserStatusUpdateRequest,
    UserUpdateRequest,
)
from app.schemas.user import UserRoleUpdateRequest

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_permission
from app.controllers.user_controller import UserController
from app.schemas.common import APIResponse
from app.schemas.user import UserRoleUpdateRequest, UserRoleUpdateResponse
router = APIRouter(
    prefix="/api",
    tags=["Users"],
)


# ============================================================
# USER LIST
# ============================================================

@router.get(
    "/organizations/{organization_id}/users",
    response_model=UserListResponse,
    summary="List organization users",
)
def list_users(
    organization_id: str,

    page: int = 1,

    page_size: int = 20,

    search: str | None = None,

    status: str | None = None,

    role: str | None = None,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("USER_VIEW")
    ),
):

    try:

        return UserController.list_users(
            db=db,
            organization_id=organization_id,
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            role=role,
        )

    except ValueError as exc:

        message = str(exc)

        status_code = (
            404
            if message == "Organization not found"
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=message,
        )


# ============================================================
# ADD USER
# ============================================================

@router.post(
    "/organizations/{organization_id}/users",
    response_model=UserCreateResponse,
    summary="Add user to organization",
)
def create_user(
    organization_id: str,

    request: UserCreateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("USER_CREATE")
    ),
):

    try:

        return UserController.create_user(
            db=db,
            organization_id=organization_id,
            request=request,
        )

    except ValueError as exc:

        message = str(exc)

        status_code = (
            404
            if "not found" in message.lower()
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=message,
        )


# ============================================================
# USER DETAILS
# ============================================================

@router.get(
    "/users/{user_id}",
    response_model=UserDetailsResponse,
    summary="Get user details",
)
def get_user_details(
    user_id: str,

    organization_id: str,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("USER_VIEW")
    ),
):

    try:

        return UserController.get_user_details(
            db=db,
            organization_id=organization_id,
            user_id=user_id,
        )

    except ValueError as exc:

        message = str(exc)

        status_code = (
            404
            if (
                "not found" in message.lower()
                or "does not belong" in message.lower()
            )
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=message,
        )


# ============================================================
# EDIT USER
# ============================================================

@router.patch(
    "/users/{user_id}",
    response_model=UserDetailsResponse,
    summary="Update user",
)
def update_user(
    user_id: str,

    organization_id: str,

    request: UserUpdateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("USER_UPDATE")
    ),
):

    try:

        return UserController.update_user(
            db=db,
            organization_id=organization_id,
            user_id=user_id,
            request=request,
        )

    except ValueError as exc:

        message = str(exc)

        status_code = (
            404
            if (
                "not found" in message.lower()
                or "does not belong" in message.lower()
            )
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=message,
        )


# ============================================================
# ACTIVATE / DEACTIVATE USER
# ============================================================

@router.patch(
    "/users/{user_id}/status",
    response_model=UserStatusResponse,
    summary="Activate or deactivate user",
)
def update_user_status(
    user_id: str,

    organization_id: str,

    request: UserStatusUpdateRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("USER_UPDATE")
    ),
):

    try:

        return UserController.update_user_status(
            db=db,
            organization_id=organization_id,
            user_id=user_id,
            request=request,
        )

    except ValueError as exc:

        message = str(exc)

        status_code = (
            404
            if (
                "not found" in message.lower()
                or "does not belong" in message.lower()
            )
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=message,
        )
@router.get("/{user_id}/projects")
def get_user_projects(
    user_id: str,
    organization_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("USER_VIEW")),
):
    return UserController.get_user_projects(
        db=db,
        organization_id=organization_id,
        user_id=user_id,
    )


@router.get("/{user_id}/activity")
def get_user_activity(
    user_id: str,
    organization_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("USER_VIEW")),
):
    return UserController.get_user_activity(
        db=db,
        organization_id=organization_id,
        user_id=user_id,
    )

@router.patch(
    "/organizations/{organization_id}/users/{user_id}/role",
    response_model=APIResponse[UserRoleUpdateResponse],
    summary="Assign user role"
)
def assign_user_role(
    organization_id: str,
    user_id: str,
    request: UserRoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("USER_UPDATE")
    )
):
    try:

        data = UserController.assign_role(
            db=db,
            organization_id=organization_id,
            user_id=user_id,
            role_id=request.role_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "User role assigned successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "not found" in str(exc).lower():
            status_code = 404

        if "does not belong" in str(exc).lower():
            status_code = 404

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )