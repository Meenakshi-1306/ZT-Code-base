from sqlalchemy.orm import Session

from app.services.rbac_service import RBACService


class RBACController:

    @staticmethod
    def list_roles(
        db: Session,
        organization_id: str
    ):
        return RBACService.list_roles(
            db,
            organization_id
        )

    @staticmethod
    def create_role(
        db: Session,
        organization_id: str,
        name: str,
        description: str | None
    ):
        return RBACService.create_role(
            db=db,
            organization_id=organization_id,
            name=name,
            description=description
        )

    @staticmethod
    def get_role(
        db: Session,
        organization_id: str,
        role_id: str
    ):
        return RBACService.get_role(
            db,
            organization_id,
            role_id
        )

    @staticmethod
    def update_role(
        db: Session,
        organization_id: str,
        role_id: str,
        update_data: dict
    ):
        return RBACService.update_role(
            db=db,
            organization_id=organization_id,
            role_id=role_id,
            update_data=update_data
        )

    @staticmethod
    def delete_role(
        db: Session,
        organization_id: str,
        role_id: str
    ):
        return RBACService.delete_role(
            db,
            organization_id,
            role_id
        )

    @staticmethod
    def list_permissions(
        db: Session
    ):
        return RBACService.list_permissions(db)

    @staticmethod
    def assign_permissions(
        db: Session,
        organization_id: str,
        role_id: str,
        permission_ids: list[str]
    ):
        return RBACService.assign_permissions(
            db=db,
            organization_id=organization_id,
            role_id=role_id,
            permission_ids=permission_ids
        )

    @staticmethod
    def remove_permission(
        db: Session,
        organization_id: str,
        role_id: str,
        permission_id: str
    ):
        return RBACService.remove_permission(
            db=db,
            organization_id=organization_id,
            role_id=role_id,
            permission_id=permission_id
        )