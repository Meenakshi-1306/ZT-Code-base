from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:

    @staticmethod
    def get_organization(
        db: Session,
        organization_id: str
    ) -> Organization | None:
        return (
            db.query(Organization)
            .filter(
                Organization.id == organization_id
            )
            .first()
        )

    @staticmethod
    def get_members(
        db: Session,
        organization_id: str
    ):
        organization = (
            db.query(Organization)
            .filter(
                Organization.id == organization_id
            )
            .first()
        )

        if not organization:
            return []

        return organization.members

    @staticmethod
    def get_membership(
        db: Session,
        user_id: str,
        organization_id: str
    ):
        from app.models.organization_member import OrganizationMember

        return (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.status == "active"
            )
            .first()
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ) -> Organization | None:
        return (
            db.query(Organization)
            .filter(
                Organization.contact_email == email
            )
            .first()
        )

    @staticmethod
    def get_by_registration_number(
        db: Session,
        registration_number: str
    ) -> Organization | None:
        return (
            db.query(Organization)
            .filter(
                Organization.registration_number
                == registration_number
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        organization: Organization
    ) -> Organization:
        db.add(organization)
        db.commit()
        db.refresh(organization)

        return organization

    @staticmethod
    def update_organization(
        db: Session,
        organization: Organization,
        update_data: dict
    ) -> Organization:

        for field, value in update_data.items():
            if hasattr(organization, field):
                setattr(
                    organization,
                    field,
                    value
                )

        db.commit()
        db.refresh(organization)

        return organization

    @staticmethod
    def mark_email_verified(
        db: Session,
        organization: Organization
    ) -> Organization:

        organization.email_verified = True
        organization.verification_status = "EMAIL_VERIFIED"

        db.commit()
        db.refresh(organization)

        return organization

    @staticmethod
    def update_verification_status(
        db: Session,
        organization: Organization,
        status: str
    ) -> Organization:

        organization.verification_status = status

        db.commit()
        db.refresh(organization)

        return organization
from app.models.organization_member import OrganizationMember
from app.models.team import Team
def count_users(
    self,
    organization_id: str,
) -> int:
        return (
        self.db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id
            == organization_id
        )
        .count()
    )


def count_teams(
    self,
    organization_id: str,
) -> int:
    return (
        self.db.query(Team)
        .filter(
            Team.organization_id
            == organization_id
        )
        .count()
    )
@staticmethod
def update_member_role(
    db: Session,
    membership,
    role_id: str
):
    membership.role_id = role_id

    db.commit()
    db.refresh(membership)

    return membership