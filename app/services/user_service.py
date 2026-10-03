import secrets
from datetime import datetime

from pwdlib import PasswordHash

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization_member import OrganizationMember
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.user_repository import (
    UserRepository,
)


class UserService:

    password_hash = PasswordHash.recommended()

    # ============================================================
    # ID GENERATION
    # ============================================================

    @staticmethod
    def generate_user_id(
        db: Session,
    ):

        while True:

            user_id = (
                f"USR_{secrets.token_hex(5).upper()}"
            )

            existing = UserRepository.get_user(
                db,
                user_id,
            )

            if not existing:
                return user_id

    # ============================================================
    # USER LIST
    # ============================================================

    @staticmethod
    def list_users(
        db: Session,
        organization_id: str,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: str | None = None,
        role: str | None = None,
    ):

        organization = (
            OrganizationRepository.get_organization(
                db,
                organization_id,
            )
        )

        if not organization:
            raise ValueError(
                "Organization not found"
            )

        if page < 1:
            page = 1

        if page_size < 1:
            page_size = 20

        if page_size > 100:
            page_size = 100

        rows = UserRepository.get_organization_users(
            db=db,
            organization_id=organization_id,
            search=search,
            status=status,
            role=role,
        )

        total = len(rows)

        start = (
            page - 1
        ) * page_size

        end = start + page_size

        paginated_rows = rows[start:end]

        users = []

        for user, membership, role_object in paginated_rows:

            team_ids = UserRepository.get_user_team_ids(
                db=db,
                user_id=user.id,
                organization_id=organization_id,
            )

            users.append(
                {
                    "user_id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role_id": (
                        role_object.id
                        if role_object
                        else None
                    ),
                    "role_name": (
                        role_object.name
                        if role_object
                        else None
                    ),
                    "status": membership.status,
                    "team_ids": team_ids,
                }
            )

        return {
            "organization_id": organization_id,
            "users": users,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    # ============================================================
    # ADD USER
    # ============================================================

    @staticmethod
    def create_user(
        db: Session,
        organization_id: str,
        name: str,
        email: str,
        role_id: str | None = None,
    ):

        organization = (
            OrganizationRepository.get_organization(
                db,
                organization_id,
            )
        )

        if not organization:
            raise ValueError(
                "Organization not found"
            )

        email = email.strip().lower()

        existing_user = (
            UserRepository.get_user_by_email(
                db,
                email,
            )
        )

        # --------------------------------------------------------
        # Existing user
        # --------------------------------------------------------

        if existing_user:

            existing_membership = (
                UserRepository.get_membership(
                    db,
                    organization_id,
                    existing_user.id,
                )
            )

            if existing_membership:

                raise ValueError(
                    "User already belongs to this organization"
                )

            user = existing_user

        # --------------------------------------------------------
        # New user
        # --------------------------------------------------------

        else:

            user_id = UserService.generate_user_id(
                db
            )

            # Temporary random password.
            #
            # The invitation/activation flow can later replace
            # this with an invitation-token based password setup.

            temporary_password = secrets.token_urlsafe(32)

            password_hash = (
                UserService.password_hash.hash(
                    temporary_password
                )
            )

            user = User(
                id=user_id,
                name=name.strip(),
                email=email,
                password_hash=password_hash,
                account_mode="organization",
                email_verified=False,
                status="pending",
            )

            user = UserRepository.create_user(
                db,
                user,
            )

        # --------------------------------------------------------
        # Create organization membership
        # --------------------------------------------------------

        membership_id = (
            f"OM_{secrets.token_hex(5).upper()}"
        )

        membership = OrganizationMember(
            id=membership_id,
            organization_id=organization_id,
            user_id=user.id,
            role_id=role_id,
            status="invited",
        )

        membership = (
            UserRepository.create_membership(
                db,
                membership,
            )
        )

        return {
            "success": True,
            "user_id": user.id,
            "organization_id": organization_id,
            "status": membership.status,
            "role_id": membership.role_id,
            "message": (
                "User invited successfully"
            ),
        }

    # ============================================================
    # USER DETAILS
    # ============================================================

    @staticmethod
    def get_user_details(
        db: Session,
        organization_id: str,
        user_id: str,
    ):

        organization = (
            OrganizationRepository.get_organization(
                db,
                organization_id,
            )
        )

        if not organization:
            raise ValueError(
                "Organization not found"
            )

        membership = (
            UserRepository.get_membership(
                db,
                organization_id,
                user_id,
            )
        )

        if not membership:
            raise ValueError(
                "User does not belong to this organization"
            )

        user = UserRepository.get_user(
            db,
            user_id,
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        role_object = membership.role

        teams = UserRepository.get_user_teams(
            db=db,
            user_id=user_id,
            organization_id=organization_id,
        )

        return {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "status": membership.status,
            "email_verified": user.email_verified,
            "account_mode": user.account_mode,

            "role": (
                {
                    "role_id": role_object.id,
                    "name": role_object.name,
                }
                if role_object
                else None
            ),

            "teams": [
                {
                    "team_id": team.id,
                    "name": team.name,
                }
                for team in teams
            ],

            # Projects belong to Module 3.
            "projects": [],

            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    # ============================================================
    # UPDATE USER
    # ============================================================

    @staticmethod
    def update_user(
        db: Session,
        organization_id: str,
        user_id: str,
        update_data: dict,
    ):

        membership = (
            UserRepository.get_membership(
                db,
                organization_id,
                user_id,
            )
        )

        if not membership:
            raise ValueError(
                "User does not belong to this organization"
            )

        user = UserRepository.get_user(
            db,
            user_id,
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        # --------------------------------------------------------
        # User fields
        # --------------------------------------------------------

        user_update = {}

        if "name" in update_data:

            if update_data["name"] is not None:

                user_update["name"] = (
                    update_data["name"].strip()
                )

        if "email" in update_data:

            if update_data["email"] is not None:

                new_email = (
                    update_data["email"]
                    .strip()
                    .lower()
                )

                existing_email_user = (
                    UserRepository.get_user_by_email(
                        db,
                        new_email,
                    )
                )

                if (
                    existing_email_user
                    and existing_email_user.id
                    != user_id
                ):
                    raise ValueError(
                        "Email address is already in use"
                    )

                user_update["email"] = new_email

        if user_update:

            UserRepository.update_user(
                db,
                user,
                user_update,
            )

        # --------------------------------------------------------
        # Role
        # --------------------------------------------------------

        if "role_id" in update_data:

            membership_update = {
                "role_id": update_data["role_id"]
            }

            UserRepository.update_membership(
                db,
                membership,
                membership_update,
            )

        return UserService.get_user_details(
            db=db,
            organization_id=organization_id,
            user_id=user_id,
        )

    # ============================================================
    # ACTIVATE / DEACTIVATE USER
    # ============================================================

    @staticmethod
    def update_user_status(
        db: Session,
        organization_id: str,
        user_id: str,
        status: str,
    ):

        normalized_status = status.lower()

        allowed_statuses = {
            "active",
            "inactive",
            "suspended",
        }

        if normalized_status not in allowed_statuses:

            raise ValueError(
                "Invalid status. Allowed values: "
                "active, inactive, suspended"
            )

        membership = (
            UserRepository.get_membership(
                db,
                organization_id,
                user_id,
            )
        )

        if not membership:
            raise ValueError(
                "User does not belong to this organization"
            )

        user = UserRepository.get_user(
            db,
            user_id,
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        # --------------------------------------------------------
        # Organization membership controls organization access.
        # --------------------------------------------------------

        if normalized_status == "active":

            membership_status = "active"

            user_status = "active"

        elif normalized_status == "inactive":

            membership_status = "inactive"

            user_status = "inactive"

        else:

            # Suspended is a user-level status.
            # Keep organization membership inactive.
            membership_status = "inactive"

            user_status = "suspended"

        UserRepository.update_membership(
            db,
            membership,
            {
                "status": membership_status,
            },
        )

        UserRepository.update_user(
            db,
            user,
            {
                "status": user_status,
                "updated_at": datetime.utcnow(),
            },
        )

        return {
            "success": True,
            "user_id": user_id,
            "organization_id": organization_id,
            "status": normalized_status,
            "message": (
                "User activated successfully"
                if normalized_status == "active"
                else "User deactivated successfully"
            ),
        }
    @staticmethod
    def get_user_projects(
    db,
    organization_id,
    user_id,
):
        user = UserRepository.get_user(
        db,
        user_id,
    )

        if not user:
            raise ValueError("User not found.")

        membership = UserRepository.get_membership(
        db,
        organization_id,
        user_id,
    )

        if not membership:
            raise ValueError(
            "User does not belong to this organization."
        )

        teams = UserRepository.get_user_teams(
        db,
        user_id,
    )

        return {
        "user_id": user_id,
        "organization_id": organization_id,
        "projects": [],
        "teams": [
            {
                "team_id": team.id,
                "name": team.name,
            }
            for team in teams
        ],
        "message": "Project mapping is not yet implemented."
    }
@staticmethod
def get_user_activity(
    db,
    organization_id,
    user_id,
):
    user = UserRepository.get_user(
        db,
        user_id,
    )

    if not user:
        raise ValueError("User not found.")

    membership = UserRepository.get_membership(
        db,
        organization_id,
        user_id,
    )

    if not membership:
        raise ValueError(
            "User does not belong to this organization."
        )

    return {
        "user_id": user_id,
        "organization_id": organization_id,
        "activity": [],
        "message": "User activity will be populated from the Zero Trust event pipeline."
    }