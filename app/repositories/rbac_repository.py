from sqlalchemy.orm import Session, joinedload

from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission


class RBACRepository:

    # ========================================================
    # ROLE
    # ========================================================

    @staticmethod
    def get_role(
        db: Session,
        role_id: str
    ):
        return (
            db.query(Role)
            .options(
                joinedload(Role.permissions)
                .joinedload(RolePermission.permission)
            )
            .filter(Role.id == role_id)
            .first()
        )

    @staticmethod
    def get_role_by_name(
        db: Session,
        organization_id: str,
        name: str
    ):
        return (
            db.query(Role)
            .filter(
                Role.organization_id == organization_id,
                Role.name == name
            )
            .first()
        )

    @staticmethod
    def get_roles(
        db: Session,
        organization_id: str
    ):
        return (
            db.query(Role)
            .options(
                joinedload(Role.permissions)
                .joinedload(RolePermission.permission)
            )
            .filter(
                Role.organization_id == organization_id
            )
            .order_by(Role.name.asc())
            .all()
        )

    @staticmethod
    def create_role(
        db: Session,
        role: Role
    ):
        db.add(role)
        db.commit()
        db.refresh(role)

        return role

    @staticmethod
    def update_role(
        db: Session,
        role: Role,
        update_data: dict
    ):
        for field, value in update_data.items():
            if hasattr(role, field):
                setattr(role, field, value)

        db.commit()
        db.refresh(role)

        return role

    @staticmethod
    def delete_role(
        db: Session,
        role: Role
    ):
        db.delete(role)
        db.commit()

    # ========================================================
    # PERMISSIONS
    # ========================================================

    @staticmethod
    def get_permission(
        db: Session,
        permission_id: str
    ):
        return (
            db.query(Permission)
            .filter(Permission.id == permission_id)
            .first()
        )

    @staticmethod
    def get_permissions(
        db: Session
    ):
        return (
            db.query(Permission)
            .order_by(
                Permission.module.asc(),
                Permission.name.asc()
            )
            .all()
        )
    @staticmethod
    def get_permission_by_name(
        db: Session,
        permission_name: str
    ):
        return (
            db.query(Permission)
            .filter(
                Permission.name == permission_name
            )
            .first()
        )

    # ========================================================
    # ROLE PERMISSIONS
    # ========================================================

    @staticmethod
    def get_role_permissions(
        db: Session,
        role_id: str
    ):
        return (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id
            )
            .all()
        )

    @staticmethod
    def get_role_permission(
        db: Session,
        role_id: str,
        permission_id: str
    ):
        return (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            )
            .first()
        )

    @staticmethod
    def add_role_permission(
        db: Session,
        role_permission: RolePermission
    ):
        db.add(role_permission)
        db.commit()
        db.refresh(role_permission)

        return role_permission

    @staticmethod
    def remove_role_permission(
        db: Session,
        role_permission: RolePermission
    ):
        db.delete(role_permission)
        db.commit()

    @staticmethod
    def remove_all_role_permissions(
        db: Session,
        role_id: str
    ):
        (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id
            )
            .delete(
                synchronize_session=False
            )
        )

        db.commit()