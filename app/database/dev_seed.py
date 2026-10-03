from datetime import datetime

from app.core.security import hash_password
from app.database.database import SessionLocal

from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.team import Team
from app.models.team_member import TeamMember

from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission


ORG_PERMISSIONS = [
    "ORG_VIEW",
    "ORG_UPDATE",
    "ORG_SETTINGS_VIEW",
    "ORG_VERIFICATION_VIEW",
]


def seed_dev_data():

    db = SessionLocal()

    try:
        # =========================================================
        # 1. ORGANIZATION
        # =========================================================

        organization = db.query(Organization).filter(
            Organization.id == "ORG_001"
        ).first()

        if not organization:
            organization = Organization(
                id="ORG_001",
                name="ABC Technologies",
                registration_number="REG12345",
                industry="Technology",
                website="https://example.com",
                contact_email="admin@abc.com",
                contact_phone="9876543210",
                address="Chennai",
                verification_status="verified"
            )

            db.add(organization)

        # =========================================================
        # 2. USERS
        # =========================================================

        admin = db.query(User).filter(
            User.id == "USR_001"
        ).first()

        if not admin:
            admin = User(
                id="USR_001",
                name="Admin User",
                email="admin@abc.com",
                password_hash=hash_password("Admin@123"),
                account_mode="organization",
                email_verified=True,
                status="active"
            )

            db.add(admin)

        developer = db.query(User).filter(
            User.id == "USR_002"
        ).first()

        if not developer:
            developer = User(
                id="USR_002",
                name="Meenakshi",
                email="meenakshi@abc.com",
                password_hash=hash_password("Meenakshi@123"),
                account_mode="organization",
                email_verified=True,
                status="active"
            )

            db.add(developer)

        db.flush()

        # =========================================================
        # 3. ROLES
        # =========================================================

        admin_role = db.query(Role).filter(
            Role.id == "ROLE_001"
        ).first()

        if not admin_role:
            admin_role = Role(
                id="ROLE_001",
                organization_id="ORG_001",
                name="Organization Admin",
                description="Full organization management access",
                is_system_role=True
            )

            db.add(admin_role)

        developer_role = db.query(Role).filter(
            Role.id == "ROLE_002"
        ).first()

        if not developer_role:
            developer_role = Role(
                id="ROLE_002",
                organization_id="ORG_001",
                name="Developer",
                description="Developer access",
                is_system_role=True
            )

            db.add(developer_role)

        db.flush()

        # =========================================================
        # 4. ORGANIZATION MEMBERS
        # =========================================================

        admin_membership = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == "ORG_001",
            OrganizationMember.user_id == "USR_001"
        ).first()

        if not admin_membership:
            admin_membership = OrganizationMember(
                id="MEM_001",
                organization_id="ORG_001",
                user_id="USR_001",
                role_id="ROLE_001",
                status="active",
                joined_at=datetime.utcnow()
            )

            db.add(admin_membership)

        developer_membership = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == "ORG_001",
            OrganizationMember.user_id == "USR_002"
        ).first()

        if not developer_membership:
            developer_membership = OrganizationMember(
                id="MEM_002",
                organization_id="ORG_001",
                user_id="USR_002",
                role_id="ROLE_002",
                status="active",
                joined_at=datetime.utcnow()
            )

            db.add(developer_membership)

        # =========================================================
        # 5. TEAM
        # =========================================================

        team = db.query(Team).filter(
            Team.id == "TEAM_001"
        ).first()

        if not team:
            team = Team(
                id="TEAM_001",
                organization_id="ORG_001",
                name="Backend Team",
                description="Backend development team",
                status="active"
            )

            db.add(team)

        db.flush()

        # =========================================================
        # 6. TEAM MEMBER
        # =========================================================

        team_member = db.query(TeamMember).filter(
            TeamMember.team_id == "TEAM_001",
            TeamMember.user_id == "USR_002"
        ).first()

        if not team_member:
            team_member = TeamMember(
                team_id="TEAM_001",
                user_id="USR_002",
                status="active",
                joined_at=datetime.utcnow()
            )

            db.add(team_member)

        # =========================================================
        # 7. ROLE PERMISSIONS
        # =========================================================

        permissions = db.query(Permission).filter(
            Permission.name.in_(ORG_PERMISSIONS + ["TEAM_MEMBER_MANAGE", "TEAM_VIEW", "ANALYTICS_VIEW", "RISK_VIEW", "ANOMALY_VIEW"])
        ).all()

        for permission in permissions:
            role_permission = db.query(RolePermission).filter(
                RolePermission.role_id == "ROLE_001",
                RolePermission.permission_id == permission.id
            ).first()

            if not role_permission:
                db.add(RolePermission(
                    role_id="ROLE_001",
                    permission_id=permission.id
                ))

        # =========================================================
        # COMMIT
        # =========================================================

        db.commit()

        print("===================================")
        print("Development data seeded successfully")
        print("===================================")
        print("Organization : ORG_001")
        print("Admin        : USR_001")
        print("Developer    : USR_002")
        print("Team         : TEAM_001")
        print("===================================")

    except Exception as e:

        db.rollback()

        print("Seed failed:")
        print(e)

        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_dev_data()