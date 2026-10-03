import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.database import engine
from app.api.routes.data_sources import router as data_source_router

Base.metadata.create_all(bind=engine)

test_app = FastAPI()
test_app.include_router(data_source_router)


class TestDataSourcesAPIs(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(test_app)

    def test_file_upload_and_list(self):
        # 1. POST /api/data-sources/files
        files = {
            'file': ('authentication_logs.csv', b'timestamp,event\n2026-09-22,LOGIN', 'text/csv')
        }
        data = {
            'name': 'Authentication Logs',
            'event_type': 'AUTHENTICATION'
        }
        response = self.client.post("/api/data-sources/files", files=files, data=data)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertTrue(res_json["success"])
        self.assertTrue(res_json["source_id"].startswith("FILE_"))
        self.assertEqual(res_json["name"], "Authentication Logs")
        self.assertEqual(res_json["file_name"], "authentication_logs.csv")
        self.assertEqual(res_json["format"], "CSV")
        self.assertEqual(res_json["status"], "READY")

        # 2. GET /api/data-sources/files
        get_res = self.client.get("/api/data-sources/files")
        self.assertEqual(get_res.status_code, 200)
        get_json = get_res.json()
        self.assertTrue(get_json["success"])
        self.assertTrue(len(get_json["sources"]) > 0)
        source = get_json["sources"][0]
        self.assertIn("source_id", source)
        self.assertIn("name", source)
        self.assertIn("file_name", source)
        self.assertIn("format", source)
        self.assertIn("records", source)
        self.assertIn("status", source)

    def test_database_connection_and_list(self):
        # 1. POST PostgreSQL
        pg_req = {
            "name": "Customer PostgreSQL",
            "database_type": "POSTGRESQL",
            "connection_string": "postgresql://user:password@host:5432/security_db"
        }
        res_pg = self.client.post("/api/data-sources/databases", json=pg_req)
        self.assertEqual(res_pg.status_code, 200)
        pg_json = res_pg.json()
        self.assertTrue(pg_json["success"])
        self.assertTrue(pg_json["source_id"].startswith("DB_"))
        self.assertEqual(pg_json["name"], "Customer PostgreSQL")
        self.assertEqual(pg_json["database_type"], "POSTGRESQL")
        self.assertEqual(pg_json["status"], "CONNECTED")
        self.assertIsInstance(pg_json["tables"], list)

        # 2. POST SQLite
        sqlite_req = {
            "name": "Internal SQLite",
            "database_type": "SQLITE",
            "database_file": "/data/security.db"
        }
        res_sq = self.client.post("/api/data-sources/databases", json=sqlite_req)
        self.assertEqual(res_sq.status_code, 200)

        # 3. GET /api/data-sources/databases
        get_res = self.client.get("/api/data-sources/databases")
        self.assertEqual(get_res.status_code, 200)
        get_json = get_res.json()
        self.assertTrue(get_json["success"])
        self.assertTrue(len(get_json["sources"]) >= 2)

    def test_api_webhook_and_list(self):
        # 1. POST API
        api_req = {
            "name": "Customer Security API",
            "type": "API",
            "url": "https://customer.example.com/api/events",
            "method": "GET",
            "authentication": {
                "type": "BEARER",
                "token": "********"
            },
            "event_type": "SECURITY_EVENT"
        }
        res_api = self.client.post("/api/data-sources/apis", json=api_req)
        self.assertEqual(res_api.status_code, 200)
        api_json = res_api.json()
        self.assertTrue(api_json["success"])
        self.assertTrue(api_json["source_id"].startswith("API_"))
        self.assertEqual(api_json["type"], "API")
        self.assertIsNone(api_json["webhook_url"])

        # 2. POST Webhook
        wh_req = {
            "name": "Customer Webhook",
            "type": "WEBHOOK",
            "event_type": "AUTHENTICATION"
        }
        res_wh = self.client.post("/api/data-sources/apis", json=wh_req)
        self.assertEqual(res_wh.status_code, 200)
        wh_json = res_wh.json()
        self.assertTrue(wh_json["success"])
        self.assertTrue(wh_json["source_id"].startswith("WH_"))
        self.assertEqual(wh_json["type"], "WEBHOOK")
        self.assertTrue(wh_json["webhook_url"].startswith("/api/webhooks/"))

        # 3. GET /api/data-sources/apis
        get_res = self.client.get("/api/data-sources/apis")
        self.assertEqual(get_res.status_code, 200)
        get_json = get_res.json()
        self.assertTrue(get_json["success"])
        self.assertTrue(len(get_json["sources"]) >= 2)

    def test_stream_and_list(self):
        # 1. POST Stream
        stream_req = {
            "name": "Security Event Stream",
            "stream_type": "KAFKA",
            "broker": "kafka.example.com:9092",
            "topic": "security-events",
            "event_type": "SECURITY_EVENT"
        }
        res = self.client.post("/api/data-sources/streams", json=stream_req)
        self.assertEqual(res.status_code, 200)
        st_json = res.json()
        self.assertTrue(st_json["success"])
        self.assertTrue(st_json["source_id"].startswith("STREAM_"))
        self.assertEqual(st_json["stream_type"], "KAFKA")
        self.assertEqual(st_json["status"], "CONNECTED")
        self.assertEqual(st_json["topic"], "security-events")

        # 2. GET /api/data-sources/streams
        get_res = self.client.get("/api/data-sources/streams")
        self.assertEqual(get_res.status_code, 200)
        get_json = get_res.json()
        self.assertTrue(get_json["success"])
        self.assertTrue(len(get_json["sources"]) >= 1)
        src = get_json["sources"][0]
        self.assertEqual(src["status"], "RUNNING")
        self.assertIn("events_received", src)


if __name__ == "__main__":
    unittest.main()
