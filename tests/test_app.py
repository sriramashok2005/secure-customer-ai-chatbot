
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invoice_preview_requires_authentication():
    response = client.post(
        "/invoices/preview",
        json={
            "invoice_number": "TEST-INV-001",
            "invoice_date": "2026-10-23",
            "amount": 500,
            "currency": "INR",
            "payment_status": "unpaid",
        },
    )

    assert response.status_code == 401


def test_invoice_create_requires_authentication():
    response = client.post(
        "/invoices/create?confirmed=true",
        json={
            "invoice_number": "TEST-INV-002",
            "invoice_date": "2026-10-23",
            "amount": 500,
            "currency": "INR",
            "payment_status": "unpaid",
        },
    )

    assert response.status_code == 401


def test_chat_conversation_routes_require_authentication():
    response = client.get("/chat/conversations")

    assert response.status_code == 401


def test_conversation_messages_require_authentication():
    response = client.get("/chat/conversations/999999/messages")

    assert response.status_code == 401
