from fastapi.testclient import TestClient

from app.main import app


def test_root_check() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Silverbird BigMama Restaurant is running.",
        "docs_url": "/docs",
        "health_url": "/health",
        "api_base": "/api/v1",
    }


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
