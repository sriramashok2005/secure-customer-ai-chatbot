
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.embedding_service import create_embedding
from app.models import Invoice, InvoiceEmbedding


def invoice_to_text(invoice: Invoice) -> str:
    """Convert an invoice into searchable text."""

    return (
        f"Invoice number: {invoice.invoice_number}. "
        f"Customer ID: {invoice.customer_id}. "
        f"Invoice date: {invoice.invoice_date.isoformat()}. "
        f"Amount: {invoice.amount} {invoice.currency}. "
        f"Payment status: {invoice.payment_status}."
    )


def index_invoice(db: Session, invoice: Invoice) -> None:
    """Create or update the vector for one invoice."""

    content = invoice_to_text(invoice)
    embedding = create_embedding(content)

    stored = db.scalar(
        select(InvoiceEmbedding).where(
            InvoiceEmbedding.invoice_id == invoice.id
        )
    )

    if stored is None:
        stored = InvoiceEmbedding(
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            content=content,
            embedding=embedding,
        )
        db.add(stored)
    else:
        stored.customer_id = invoice.customer_id
        stored.content = content
        stored.embedding = embedding


def index_all_invoices(db: Session) -> dict:
    """Index every invoice, without creating duplicate vector rows."""

    invoices = db.scalars(
        select(Invoice).order_by(Invoice.id)
    ).all()

    indexed = 0

    try:
        for invoice in invoices:
            index_invoice(db, invoice)
            indexed += 1

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Invoice indexing completed.",
        "indexed_invoices": indexed,
    }
