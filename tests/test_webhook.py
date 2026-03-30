"""Tests for FastAPI webhook endpoint."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from main import app

    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_webhook_missing_body(client):
    """Test webhook returns 400 when Body is missing."""
    response = client.post(
        "/webhook",
        data={"From": "whatsapp:+14155238886"},
    )
    assert response.status_code == 400


def test_webhook_missing_from(client):
    """Test webhook returns 400 when From is missing."""
    response = client.post(
        "/webhook",
        data={"Body": "Hello!"},
    )
    assert response.status_code == 400


def test_webhook_empty_body(client):
    """Test webhook returns 400 when Body is empty."""
    response = client.post(
        "/webhook",
        data={"From": "whatsapp:+14155238886", "Body": ""},
    )
    assert response.status_code == 400


def test_webhook_valid_request(client):
    """Test webhook processes valid request and returns TwiML response."""
    response = client.post(
        "/webhook",
        data={
            "From": "whatsapp:+14155238886",
            "To": "whatsapp:+14155238887",
            "Body": "Hello!",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/xml; charset=utf-8"
    assert "<Message>" in response.text
