from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_permission

from app.controllers.rbac_controller import RBACController

from app.schemas.rbac import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleResponse,
    RoleListResponse,
    PermissionListResponse,
    RolePermissionRequest,
    RolePermissionResponse
)


router = APIRouter(
    prefix="/api",
    tags=["RBAC"]
)


# ============================================================
# ROLES
# ============================================================

@router.get(
    "/organizations/{organization_id}/roles",
    response_model=RoleListResponse,
    dependencies=[
        Depends(require_permission("ROLE_VIEW"))
    ]
)
def list_roles(
    organization_id: str,
    db: Session = Depends(get_db)
):
    try:
        return RBACController.list_roles(
            db,
            organization_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )


@router.post(
    "/organizations/{organization_id}/roles",
    response_model=RoleResponse,
    dependencies=[
        Depends(require_permission("ROLE_CREATE"))
    ]
)
def create_role(
    organization_id: str,
    request: RoleCreateRequest,
    db: Session = Depends(get_db)
):
    try:
        return RBACController.create_role(
            db=db,
            organization_id=organization_id,
            name=request.name,
            description=request.description
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.get(
    "/organizations/{organization_id}/roles/{role_id}",
    response_model=RoleResponse,
    dependencies=[
        Depends(require_permission("ROLE_VIEW"))
    ]
)
def get_role(
    organization_id: str,
    role_id: str,
    db: Session = Depends(get_db)
):
    try:
        return RBACController.get_role(
            db,
            organization_id,
            role_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )


@router.patch(
    "/organizations/{organization_id}/roles/{role_id}",
    response_model=RoleResponse,
    dependencies=[
        Depends(require_permission("ROLE_UPDATE"))
    ]
)
def update_role(
    organization_id: str,
    role_id: str,
    request: RoleUpdateRequest,
    db: Session = Depends(get_db)
):
    try:
        return RBACController.update_role(
            db=db,
            organization_id=organization_id,
            role_id=role_id,
            update_data=request.model_dump(
                exclude_unset=True
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.delete(
    "/organizations/{organization_id}/roles/{role_id}",
    dependencies=[
        Depends(require_permission("ROLE_DELETE"))
    ]
)
def delete_role(
    organization_id: str,
    role_id: str,
    db: Session = Depends(get_db)
):
    try:
        return RBACController.delete_role(
            db,
            organization_id,
            role_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


# ============================================================
# PERMISSIONS
# ============================================================

@router.get(
    "/permissions",
    response_model=PermissionListResponse,
    dependencies=[
        Depends(require_permission("ROLE_VIEW"))
    ]
)
def list_permissions(
    db: Session = Depends(get_db)
):
    return RBACController.list_permissions(db)


# ============================================================
# ROLE → PERMISSIONS
# ============================================================

@router.put(
    "/organizations/{organization_id}/roles/{role_id}/permissions",
    response_model=RolePermissionResponse,
    dependencies=[
        Depends(require_permission("ROLE_UPDATE"))
    ]
)
def assign_permissions(
    organization_id: str,
    role_id: str,
    request: RolePermissionRequest,
    db: Session = Depends(get_db)
):
    try:
        return RBACController.assign_permissions(
            db=db,
            organization_id=organization_id,
            role_id=role_id,
            permission_ids=request.permission_ids
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.delete(
    "/organizations/{organization_id}/roles/{role_id}/permissions/{permission_id}",
    dependencies=[
        Depends(require_permission("ROLE_UPDATE"))
    ]
)
def remove_permission(
    organization_id: str,
    role_id: str,
    permission_id: str,
    db: Session = Depends(get_db)
):
    try:
        return RBACController.remove_permission(
            db=db,
            organization_id=organization_id,
            role_id=role_id,
            permission_id=permission_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )