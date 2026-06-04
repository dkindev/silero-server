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
    """Test that /health returns 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_returns_ok_status(client: TestClient):
    """Test that /health returns correct JSON response."""
    response = client.get("/health")
    data = response.json()
    assert data == {"status": "ok"}


def test_health_check_response_schema(client: TestClient):
    """Test that /health response has correct schema."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert isinstance(data["status"], str)


def test_head_health_returns_200_no_body(client: TestClient):
    """Test that HEAD /health returns 200 with no body."""
    response = client.head("/health")
    assert response.status_code == 200
    assert response.content == b""


def test_old_api_v1_health_returns_404(client: TestClient):
    """Test that old /api/v1/health path returns 404."""
    response = client.get("/api/v1/health")
    assert response.status_code == 404
