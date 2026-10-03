from fastapi.testclient import TestClient

from app.database.seed import seed_permissions
from app.database.dev_seed import seed_dev_data
from app.main import app

client = TestClient(app)


def setup_module():
    seed_permissions()
    seed_dev_data()


def get_token(email: str, password: str):
    response = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_organization_details_are_available_to_org_admin():
    token = get_token("admin@abc.com", "Admin@123")
    response = client.get(
        "/api/organizations/ORG_001",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()["data"]
    assert payload["organization_id"] == "ORG_001"
    assert payload["name"] == "ABC Technologies"
    assert payload["verification_status"] == "verified"


def test_organization_profile_update_requires_permission():
    admin_token = get_token("admin@abc.com", "Admin@123")
    dev_token = get_token("meenakshi@abc.com", "Meenakshi@123")

    success = client.patch(
        "/api/organizations/ORG_001",
        json={"name": "ABC Technologies Updated", "industry": "Cyber Security"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert success.status_code == 200, success.text

    denied = client.patch(
        "/api/organizations/ORG_001",
        json={"name": "Blocked Update"},
        headers={"Authorization": f"Bearer {dev_token}"},
    )
    assert denied.status_code == 403, denied.text


def test_organization_settings_and_verification_endpoints_are_exposed():
    token = get_token("admin@abc.com", "Admin@123")

    settings = client.get(
        "/api/organizations/ORG_001/settings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert settings.status_code == 200, settings.text

    verification = client.get(
        "/api/organizations/ORG_001/verification",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert verification.status_code == 200, verification.text
    assert verification.json()["data"]["organization_id"] == "ORG_001"
