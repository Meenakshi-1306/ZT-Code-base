import traceback
from fastapi.testclient import TestClient
from app.main import app

try:
    client = TestClient(app)
    response = client.post('/api/auth/login', data={'username': 'admin@abc.com', 'password': 'Admin@123'})
    print('STATUS', response.status_code)
    print('TEXT', response.text)
    print('JSON', response.json())
except Exception:
    traceback.print_exc()
    raise
