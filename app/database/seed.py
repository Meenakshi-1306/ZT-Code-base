from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.permission import Permission


PERMISSIONS = [
    ("PERM_001", "USER_VIEW", "View organization users", "users"),
    ("PERM_002", "USER_CREATE", "Create organization users", "users"),
    ("PERM_003", "USER_UPDATE", "Update organization users", "users"),
    ("PERM_004", "USER_DELETE", "Delete organization users", "users"),

    ("PERM_005", "ROLE_VIEW", "View roles", "roles"),
    ("PERM_006", "ROLE_CREATE", "Create roles", "roles"),
    ("PERM_007", "ROLE_UPDATE", "Update roles", "roles"),
    ("PERM_008", "ROLE_DELETE", "Delete roles", "roles"),

    ("PERM_009", "TEAM_VIEW", "View teams", "teams"),
    ("PERM_010", "TEAM_CREATE", "Create teams", "teams"),
    ("PERM_011", "TEAM_UPDATE", "Update teams", "teams"),
    ("PERM_012", "TEAM_DELETE", "Delete teams", "teams"),
    ("PERM_013", "TEAM_MEMBER_MANAGE", "Manage team members", "teams"),

    ("PERM_014", "ANALYTICS_VIEW", "View analytics", "analytics"),
    ("PERM_015", "ALERT_VIEW", "View security alerts", "security"),
    ("PERM_016", "RISK_VIEW", "View risk information", "security"),
    ("PERM_017", "ANOMALY_VIEW", "View anomalies", "security"),

    ("PERM_018", "ORG_VIEW", "View organization details", "organization"),
    ("PERM_019", "ORG_UPDATE", "Update organization profile", "organization"),
    ("PERM_020", "ORG_SETTINGS_VIEW", "View organization settings", "organization"),
    ("PERM_021", "ORG_VERIFICATION_VIEW", "View organization verification", "organization"),
]


def seed_permissions():
    db: Session = SessionLocal()

    try:
        for permission_id, name, description, module in PERMISSIONS:

            existing = (
                db.query(Permission)
                .filter(Permission.name == name)
                .first()
            )

            if existing:
                continue

            permission = Permission(
                id=permission_id,
                name=name,
                description=description,
                module=module
            )

            db.add(permission)

        db.commit()

        print("Permissions seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_permissions()