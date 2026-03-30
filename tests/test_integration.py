"""Integration tests for full webhook-to-agent flow."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from main import app

    return TestClient(app)


class TestWebhookToAgentIntegration:
    """Integration tests for the complete WhatsApp message flow."""

    def test_create_task_via_webhook_flow(self, client, db_session):
        """Test complete flow: webhook -> agent -> create task -> TwiML response."""
        response = client.post(
            "/webhook",
            data={
                "From": "whatsapp:+14155238886",
                "To": "whatsapp:+14155238887",
                "Body": "Ask John to finish the report by Friday",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/xml; charset=utf-8"
        assert "<Message>" in response.text
        assert "<Response" in response.text

    def test_query_tasks_via_webhook_flow(self, client, db_session):
        """Test complete flow: webhook -> agent -> query tasks -> TwiML response."""
        response = client.post(
            "/webhook",
            data={
                "From": "whatsapp:+14155238886",
                "To": "whatsapp:+14155238887",
                "Body": "How many tasks does Alice have?",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/xml; charset=utf-8"
        assert "<Message>" in response.text

    def test_clarify_intent_via_webhook_flow(self, client, db_session):
        """Test complete flow: webhook -> agent -> clarify intent -> TwiML response."""
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


class TestHealthCheckIntegration:
    """Integration tests for health check endpoint."""

    def test_health_endpoint_returns_healthy(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
