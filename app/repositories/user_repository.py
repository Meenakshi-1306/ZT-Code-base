from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization_member import OrganizationMember
from app.models.role import Role
from app.models.team import Team
from app.models.team_member import TeamMember


class UserRepository:

    # ============================================================
    # USER
    # ============================================================

    @staticmethod
    def get_user(
        db: Session,
        user_id: str,
    ):
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str,
    ):
        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def create_user(
        db: Session,
        user: User,
    ):
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_user(
        db: Session,
        user: User,
        update_data: dict,
    ):
        for field, value in update_data.items():

            if hasattr(user, field):
                setattr(
                    user,
                    field,
                    value,
                )

        db.commit()
        db.refresh(user)

        return user

    # ============================================================
    # ORGANIZATION MEMBERSHIP
    # ============================================================

    @staticmethod
    def get_membership(
        db: Session,
        organization_id: str,
        user_id: str,
    ):
        return (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id
                == organization_id,

                OrganizationMember.user_id
                == user_id,
            )
            .first()
        )

    @staticmethod
    def get_organization_users(
        db: Session,
        organization_id: str,
        search: str | None = None,
        status: str | None = None,
        role: str | None = None,
    ):
        query = (
            db.query(
                User,
                OrganizationMember,
                Role,
            )
            .join(
                OrganizationMember,
                OrganizationMember.user_id == User.id,
            )
            .outerjoin(
                Role,
                Role.id == OrganizationMember.role_id,
            )
            .filter(
                OrganizationMember.organization_id
                == organization_id
            )
        )

        # --------------------------------------------------------
        # Search
        # --------------------------------------------------------

        if search:

            search_value = f"%{search}%"

            query = query.filter(
                or_(
                    User.name.ilike(search_value),
                    User.email.ilike(search_value),
                )
            )

        # --------------------------------------------------------
        # Status
        #
        # Status comes from organization membership when it is
        # invited/active/inactive.
        # --------------------------------------------------------

        if status:

            query = query.filter(
                OrganizationMember.status == status
            )

        # --------------------------------------------------------
        # Role
        #
        # Supports either role ID or role name.
        # --------------------------------------------------------

        if role:

            query = query.filter(
                or_(
                    Role.id == role,
                    Role.name.ilike(role),
                )
            )

        return query.all()

    @staticmethod
    def create_membership(
        db: Session,
        membership: OrganizationMember,
    ):
        db.add(membership)
        db.commit()
        db.refresh(membership)

        return membership

    @staticmethod
    def update_membership(
        db: Session,
        membership: OrganizationMember,
        update_data: dict,
    ):
        for field, value in update_data.items():

            if hasattr(membership, field):
                setattr(
                    membership,
                    field,
                    value,
                )

        db.commit()
        db.refresh(membership)

        return membership

    # ============================================================
    # TEAM MEMBERSHIP
    # ============================================================

    @staticmethod
    def get_user_teams(
        db: Session,
        user_id: str,
        organization_id: str,
    ):
        return (
            db.query(Team)
            .join(
                TeamMember,
                TeamMember.team_id == Team.id,
            )
            .filter(
                TeamMember.user_id == user_id,
                Team.organization_id == organization_id,
            )
            .all()
        )

    @staticmethod
    def get_user_team_ids(
        db: Session,
        user_id: str,
        organization_id: str,
    ):
        teams = UserRepository.get_user_teams(
            db=db,
            user_id=user_id,
            organization_id=organization_id,
        )

        return [
            team.id
            for team in teams
        ]