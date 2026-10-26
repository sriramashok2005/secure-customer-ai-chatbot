
from fastapi.testclient import TestClient

from main import app
from app.core.security import get_current_customer
from app.core.database import SessionLocal
from app.models import Customer, Conversation


client = TestClient(app)


def test_deepa_cannot_access_aruns_conversation():
    db = SessionLocal()

    try:
        arun = db.query(Customer).filter_by(
            email="arun.demo@example.com"
        ).first()

        deepa = db.query(Customer).filter_by(
            email="deepa.demo@example.com"
        ).first()

        assert arun is not None, "Arun seed customer not found"
        assert deepa is not None, "Deepa seed customer not found"

        arun_id = arun.id
        deepa_id = deepa.id

        conversation = Conversation(
            customer_id=arun_id,
            title="Isolation test conversation",
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        conversation_id = conversation.id

    finally:
        db.close()

    def authenticate_as_deepa():
        cleanup_db = SessionLocal()
        try:
            customer = cleanup_db.query(Customer).filter_by(
                id=deepa_id
            ).first()
            return customer
        finally:
            cleanup_db.close()

    app.dependency_overrides[get_current_customer] = authenticate_as_deepa

    try:
        response = client.get(
            f"/chat/conversations/{conversation_id}/messages"
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.pop(get_current_customer, None)

        cleanup_db = SessionLocal()
        try:
            test_conversation = cleanup_db.query(Conversation).filter_by(
                id=conversation_id
            ).first()

            if test_conversation:
                cleanup_db.delete(test_conversation)
                cleanup_db.commit()
        finally:
            cleanup_db.close()
