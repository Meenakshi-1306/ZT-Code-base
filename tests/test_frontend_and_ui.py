import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestFrontendAndUI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_root_serves_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("ZeroTrust", response.text)

    def test_ui_route_serves_html(self):
        response = self.client.get("/ui")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))

    def test_static_css_and_js(self):
        css_res = self.client.get("/static/style.css")
        self.assertEqual(css_res.status_code, 200)
        js_res = self.client.get("/static/app.js")
        self.assertEqual(js_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
