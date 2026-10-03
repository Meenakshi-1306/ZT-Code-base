from sqlalchemy.orm import Session

from app.schemas.user import (
    UserCreateRequest,
    UserStatusUpdateRequest,
    UserUpdateRequest
)

from app.services.user_service import UserService


class UserController:

    # ============================================================
    # LIST USERS
    # ============================================================

    @staticmethod
    def list_users(
        db: Session,
        organization_id: str,
        page: int,
        page_size: int,
        search: str | None = None,
        status: str | None = None,
        role: str | None = None
    ):
        return UserService.list_users(
            db=db,
            organization_id=organization_id,
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            role=role
        )

    # ============================================================
    # CREATE / INVITE USER
    # ============================================================

    @staticmethod
    def create_user(
        db: Session,
        organization_id: str,
        request: UserCreateRequest
    ):
        return UserService.create_user(
            db=db,
            organization_id=organization_id,
            name=request.name,
            email=request.email,
            role_id=request.role_id
        )

    # ============================================================
    # GET USER DETAILS
    # ============================================================

    @staticmethod
    def get_user_details(
        db: Session,
        organization_id: str,
        user_id: str
    ):
        return UserService.get_user_details(
            db=db,
            organization_id=organization_id,
            user_id=user_id
        )

    # ============================================================
    # UPDATE USER
    # ============================================================

    @staticmethod
    def update_user(
        db: Session,
        organization_id: str,
        user_id: str,
        request: UserUpdateRequest
    ):
        return UserService.update_user(
            db=db,
            organization_id=organization_id,
            user_id=user_id,
            update_data=request.model_dump(
                exclude_unset=True
            )
        )

    # ============================================================
    # UPDATE USER STATUS
    # ============================================================

    @staticmethod
    def update_user_status(
        db: Session,
        organization_id: str,
        user_id: str,
        request: UserStatusUpdateRequest
    ):
        return UserService.update_user_status(
            db=db,
            organization_id=organization_id,
            user_id=user_id,
            status=request.status
        )
    @staticmethod
    def get_user_projects(
    db,
    organization_id,
    user_id,
):
        return UserService.get_user_projects(
        db=db,
        organization_id=organization_id,
        user_id=user_id,
    )


    @staticmethod
    def get_user_activity(
    db,
    organization_id,
    user_id,
):
        return UserService.get_user_activity(
        db=db,
        organization_id=organization_id,
        user_id=user_id,
    )

    @staticmethod
    def assign_role(
    db: Session,
    organization_id: str,
    user_id: str,
    role_id: str,
    current_user
):
        return UserService.assign_role(
        db=db,
        organization_id=organization_id,
        user_id=user_id,
        role_id=role_id,
        current_user=current_user
    )