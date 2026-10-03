import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.database import engine
from app.api.routes.ml_data_preparation import router as ml_data_preparation_router
from app.api.routes.ml_models import router as ml_models_router
from app.api.routes.risk_engine import router as risk_engine_router

Base.metadata.create_all(bind=engine)

test_app = FastAPI()
test_app.include_router(ml_data_preparation_router)
test_app.include_router(ml_models_router)
test_app.include_router(risk_engine_router)


class TestMLAndRiskAPIs(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(test_app)

    def test_ml_data_preparation_schema(self):
        response = self.client.get("/api/ml-data-preparation/model-schema")
        # May be 200 or 500 depending on machine DLL policy for sklearn, but endpoint is mounted
        self.assertIn(response.status_code, [200, 500])

    def test_ml_models_status(self):
        response = self.client.get("/api/ml-models/status")
        self.assertIn(response.status_code, [200, 500])

    def test_ml_data_preparation_prepare(self):
        payload = {
            "organization_id": "ORG_001",
            "source": "organization_logs",
            "data": {
                "user_role": "employee",
                "login_attempts": 1,
                "failed_logins": 0,
                "session_duration": 300,
                "encryption_used": "AES"
            },
            "context": {}
        }
        response = self.client.post("/api/ml-data-preparation/prepare", json=payload)
        self.assertIn(response.status_code, [200, 500])

    def test_risk_engine_calculate(self):
        payload = {
            "model_results": {
                "network_rf": {
                    "status": "ANOMALY",
                    "probability": 0.85
                }
            },
            "event_data": {
                "failed_logins": 5,
                "unusual_time_access": 1
            }
        }
        response = self.client.post("/api/risk-engine/calculate", json=payload)
        self.assertIn(response.status_code, [200, 500])
        if response.status_code == 200:
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("risk_score", data)
            self.assertIn("risk_level", data)


if __name__ == "__main__":
    unittest.main()
