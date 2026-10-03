from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.role_permission import RolePermission

from app.repositories.rbac_repository import RBACRepository
from app.repositories.organization_repository import OrganizationRepository


class RBACService:

    # ========================================================
    # ROLES
    # ========================================================

    @staticmethod
    def list_roles(
        db: Session,
        organization_id: str
    ):
        organization = OrganizationRepository.get_organization(
            db,
            organization_id
        )

        if not organization:
            raise ValueError("Organization not found")

        roles = RBACRepository.get_roles(
            db,
            organization_id
        )

        result = []

        for role in roles:

            permissions = []

            for role_permission in role.permissions:

                if role_permission.permission:
                    permissions.append({
                        "id": role_permission.permission.id,
                        "name": role_permission.permission.name,
                        "description": role_permission.permission.description,
                        "module": role_permission.permission.module
                    })

            result.append({
                "id": role.id,
                "organization_id": role.organization_id,
                "name": role.name,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "created_at": role.created_at,
                "updated_at": role.updated_at,
                "permissions": permissions
            })

        return {
            "organization_id": organization_id,
            "roles": result,
            "total": len(result)
        }

    @staticmethod
    def create_role(
        db: Session,
        organization_id: str,
        name: str,
        description: str | None = None
    ):

        organization = OrganizationRepository.get_organization(
            db,
            organization_id
        )

        if not organization:
            raise ValueError("Organization not found")

        existing_role = RBACRepository.get_role_by_name(
            db,
            organization_id,
            name
        )

        if existing_role:
            raise ValueError(
                "A role with this name already exists"
            )

        role = Role(
            id=f"ROLE_{uuid4().hex[:10].upper()}",
            organization_id=organization_id,
            name=name.strip(),
            description=description,
            is_system_role=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        return RBACRepository.create_role(
            db,
            role
        )

    @staticmethod
    def get_role(
        db: Session,
        organization_id: str,
        role_id: str
    ):

        role = RBACRepository.get_role(
            db,
            role_id
        )

        if not role:
            raise ValueError("Role not found")

        if role.organization_id != organization_id:
            raise ValueError(
                "Role does not belong to this organization"
            )

        permissions = []

        for role_permission in role.permissions:

            if role_permission.permission:
                permissions.append({
                    "id": role_permission.permission.id,
                    "name": role_permission.permission.name,
                    "description": role_permission.permission.description,
                    "module": role_permission.permission.module
                })

        return {
            "id": role.id,
            "organization_id": role.organization_id,
            "name": role.name,
            "description": role.description,
            "is_system_role": role.is_system_role,
            "created_at": role.created_at,
            "updated_at": role.updated_at,
            "permissions": permissions
        }

    @staticmethod
    def update_role(
        db: Session,
        organization_id: str,
        role_id: str,
        update_data: dict
    ):

        role = RBACRepository.get_role(
            db,
            role_id
        )

        if not role:
            raise ValueError("Role not found")

        if role.organization_id != organization_id:
            raise ValueError(
                "Role does not belong to this organization"
            )

        if role.is_system_role:
            raise ValueError(
                "System roles cannot be modified"
            )

        if "name" in update_data and update_data["name"]:

            existing_role = RBACRepository.get_role_by_name(
                db,
                organization_id,
                update_data["name"]
            )

            if (
                existing_role
                and existing_role.id != role_id
            ):
                raise ValueError(
                    "A role with this name already exists"
                )

        update_data["updated_at"] = datetime.utcnow()

        return RBACRepository.update_role(
            db,
            role,
            update_data
        )

    @staticmethod
    def delete_role(
        db: Session,
        organization_id: str,
        role_id: str
    ):

        role = RBACRepository.get_role(
            db,
            role_id
        )

        if not role:
            raise ValueError("Role not found")

        if role.organization_id != organization_id:
            raise ValueError(
                "Role does not belong to this organization"
            )

        if role.is_system_role:
            raise ValueError(
                "System roles cannot be deleted"
            )

        RBACRepository.delete_role(
            db,
            role
        )

        return {
            "success": True,
            "message": "Role deleted successfully"
        }

    # ========================================================
    # PERMISSIONS
    # ========================================================

    @staticmethod
    def list_permissions(
        db: Session
    ):

        permissions = RBACRepository.get_permissions(db)

        result = []

        for permission in permissions:

            result.append({
                "id": permission.id,
                "name": permission.name,
                "description": permission.description,
                "module": permission.module
            })

        return {
            "permissions": result,
            "total": len(result)
        }

    # ========================================================
    # ASSIGN PERMISSIONS
    # ========================================================

    @staticmethod
    def assign_permissions(
        db: Session,
        organization_id: str,
        role_id: str,
        permission_ids: list[str]
    ):

        role = RBACRepository.get_role(
            db,
            role_id
        )

        if not role:
            raise ValueError("Role not found")

        if role.organization_id != organization_id:
            raise ValueError(
                "Role does not belong to this organization"
            )

        if role.is_system_role:
            raise ValueError(
                "System role permissions cannot be modified"
            )

        # Remove existing assignments
        RBACRepository.remove_all_role_permissions(
            db,
            role_id
        )

        assigned_ids = []

        for permission_id in permission_ids:

            permission = RBACRepository.get_permission(
                db,
                permission_id
            )

            if not permission:
                raise ValueError(
                    f"Permission not found: {permission_id}"
                )

            role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission_id,
                created_at=datetime.utcnow()
            )

            RBACRepository.add_role_permission(
                db,
                role_permission
            )

            assigned_ids.append(permission_id)

        return {
            "role_id": role_id,
            "permission_ids": assigned_ids,
            "message": "Role permissions updated successfully"
        }

    @staticmethod
    def remove_permission(
        db: Session,
        organization_id: str,
        role_id: str,
        permission_id: str
    ):

        role = RBACRepository.get_role(
            db,
            role_id
        )

        if not role:
            raise ValueError("Role not found")

        if role.organization_id != organization_id:
            raise ValueError(
                "Role does not belong to this organization"
            )

        if role.is_system_role:
            raise ValueError(
                "System role permissions cannot be modified"
            )

        role_permission = RBACRepository.get_role_permission(
            db,
            role_id,
            permission_id
        )

        if not role_permission:
            raise ValueError(
                "Permission is not assigned to this role"
            )

        RBACRepository.remove_role_permission(
            db,
            role_permission
        )

        return {
            "success": True,
            "message": "Permission removed from role"
        }
        # ========================================================
    # PERMISSION CHECK
    # ========================================================

    @staticmethod
    def user_has_permission(
        db: Session,
        user_id: str,
        organization_id: str,
        permission_name: str
    ) -> bool:

        # Find the permission
        permission = RBACRepository.get_permission_by_name(
            db,
            permission_name
        )

        if not permission:
            return False

        # Find the user's active organization membership
        membership = OrganizationRepository.get_membership(
            db,
            user_id,
            organization_id
        )

        if not membership:
            return False

        # User must have a role
        if not membership.role_id:
            return False

        # Check whether the role has this permission
        role_permission = RBACRepository.get_role_permission(
            db,
            membership.role_id,
            permission.id
        )

        return role_permission is not None
        # ========================================================
    # PERMISSION CHECK
    # ========================================================

    @staticmethod
    def user_has_permission(
        db: Session,
        user_id: str,
        organization_id: str,
        permission_name: str
    ) -> bool:

        permission = RBACRepository.get_permission_by_name(
            db,
            permission_name
        )

        if not permission:
            return False

        membership = OrganizationRepository.get_membership(
            db,
            user_id,
            organization_id
        )

        if not membership:
            return False

        if not membership.role_id:
            return False

        role_permission = RBACRepository.get_role_permission(
            db,
            membership.role_id,
            permission.id
        )

        return role_permission is not None