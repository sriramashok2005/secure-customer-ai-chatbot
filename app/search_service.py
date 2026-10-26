
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.embedding_service import create_embedding
from app.models import Invoice, InvoiceEmbedding


def search_invoice_records(
    db: Session,
    customer_id: int,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Search invoice records belonging only to the given customer."""

    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if top_k < 1 or top_k > 10:
        raise ValueError("top_k must be between 1 and 10.")

    query_lower = query.casefold()

    # Apply an exact payment-status filter when requested.
    status_filter = None

    if "unpaid" in query_lower:
        status_filter = "unpaid"
    elif "overdue" in query_lower:
        status_filter = "overdue"
    elif "paid" in query_lower and "unpaid" not in query_lower:
        status_filter = "paid"

    query_embedding = create_embedding(query)

    distance = InvoiceEmbedding.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    statement = (
        select(
            InvoiceEmbedding.invoice_id,
            InvoiceEmbedding.content,
            distance,
        )
        .join(
            Invoice,
            Invoice.id == InvoiceEmbedding.invoice_id,
        )
        .where(
            InvoiceEmbedding.customer_id == customer_id,
            Invoice.customer_id == customer_id,
        )
    )

    if status_filter:
        statement = statement.where(
            Invoice.payment_status == status_filter
        )

    statement = statement.order_by(distance).limit(top_k)

    results = db.execute(statement).all()

    return [
        {
            "invoice_id": row.invoice_id,
            "content": row.content,
            "distance": float(row.distance),
        }
        for row in results
    ]
