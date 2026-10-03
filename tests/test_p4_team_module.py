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


def test_get_team_details_as_admin():
    token = get_token("admin@abc.com", "Admin@123")
    response = client.get(
        "/api/teams/TEAM_001",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["team_id"] == "TEAM_001"
    assert data["organization_id"] == "ORG_001"
    assert data["lead_id"] in {None, "USR_001", "USR_002"}


def test_team_lead_assignment_requires_permission():
    admin_token = get_token("admin@abc.com", "Admin@123")
    dev_token = get_token("meenakshi@abc.com", "Meenakshi@123")

    admin_response = client.post(
        "/api/teams/TEAM_001/lead",
        json={"user_id": "USR_002"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_response.status_code == 200, admin_response.text

    denied = client.post(
        "/api/teams/TEAM_001/lead",
        json={"user_id": "USR_001"},
        headers={"Authorization": f"Bearer {dev_token}"},
    )
    assert denied.status_code == 403, denied.text


def test_security_shell_endpoints_return_empty_structures():
    token = get_token("admin@abc.com", "Admin@123")

    for endpoint, key in [
        ("/api/teams/TEAM_001/activity", "activity"),
        ("/api/teams/TEAM_001/anomalies", "anomalies"),
        ("/api/teams/TEAM_001/risk", "risk"),
        ("/api/teams/TEAM_001/analytics", "analytics"),
    ]:
        response = client.get(
            endpoint,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text
        payload = response.json()["data"]
        if key == "risk":
            assert payload[key] is None
        elif key == "analytics":
            assert payload[key] == {}
        else:
            assert payload[key] == []
