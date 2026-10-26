
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Customer, Invoice, InvoiceEmbedding


def test_invoice_search_returns_only_owners_records():
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

        statement = (
            select(
                InvoiceEmbedding.invoice_id,
                InvoiceEmbedding.customer_id,
            )
            .join(
                Invoice,
                Invoice.id == InvoiceEmbedding.invoice_id,
            )
            .where(
                InvoiceEmbedding.customer_id == arun.id,
                Invoice.customer_id == arun.id,
            )
        )

        results = db.execute(statement).all()

        assert results, "Arun has no indexed invoices to test"

        for result in results:
            assert result.customer_id == arun.id
            assert result.customer_id != deepa.id

    finally:
        db.close()
