import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create an HTTP client for testing."""

    app = FastAPI()

    from src.routers import health

    app.include_router(health.router)

    return TestClient(app)


def test_health_check_returns_200(client: TestClient):
    """Test that /api/v1/health returns 200 status code."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_check_returns_ok_status(client: TestClient):
    """Test that /api/v1/health returns correct JSON response."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert data == {"status": "ok"}


def test_health_check_response_schema(client: TestClient):
    """Test that /api/v1/health response has correct schema."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert isinstance(data["status"], str)
