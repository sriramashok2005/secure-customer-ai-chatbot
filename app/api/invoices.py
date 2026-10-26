
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.auth import get_db
from app.core.security import get_current_customer
from app.models import Customer, Invoice
from app.schemas import InvoiceCreate
from app.indexing_service import index_invoice


router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/preview")
def preview_invoice(
    data: InvoiceCreate,
    customer: Customer = Depends(get_current_customer),
):
    invoice_number = data.invoice_number.strip()

    if not invoice_number:
        raise HTTPException(
            status_code=422,
            detail="Invoice number cannot be empty.",
        )

    return {
        "message": "Review these details before creating the invoice.",
        "requires_confirmation": True,
        "invoice": {
            "invoice_number": invoice_number,
            "invoice_date": data.invoice_date.isoformat(),
            "amount": str(data.amount),
            "currency": data.currency.upper(),
            "payment_status": data.payment_status,
        },
    }


@router.post("/create", status_code=201)
def create_invoice(
    data: InvoiceCreate,
    confirmed: bool = False,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    if not confirmed:
        raise HTTPException(
            status_code=400,
            detail="Explicit confirmation is required before creating the invoice.",
        )

    invoice_number = data.invoice_number.strip()

    if not invoice_number:
        raise HTTPException(
            status_code=422,
            detail="Invoice number cannot be empty.",
        )

    existing = db.scalar(
        select(Invoice).where(
            Invoice.customer_id == customer.id,
            Invoice.invoice_number == invoice_number,
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="An invoice with this number already exists.",
        )

    invoice = Invoice(
        customer_id=customer.id,
        invoice_number=invoice_number,
        invoice_date=data.invoice_date,
        amount=data.amount,
        currency=data.currency.upper(),
        payment_status=data.payment_status,
    )

    try:
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate invoice number or invalid invoice data.",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Invoice could not be saved. Please retry.",
        )

    invoice_id = invoice.id
    try:
        index_invoice(db, invoice)
        invoice.indexing_status = "indexed"
        db.commit()
    except Exception:
        db.rollback()
        invoice = db.get(Invoice, invoice_id)
        if invoice is not None:
            invoice.indexing_status = "pending_retry"
            db.commit()
    return {
        "message": "Invoice saved.",
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "customer_id": customer.id,
        "amount": str(invoice.amount),
        "currency": invoice.currency,
        "payment_status": invoice.payment_status,
        "indexing_status": invoice.indexing_status,
    }


@router.post("/reindex")
def reindex_customer_invoices(
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
):
    invoices = db.scalars(
        select(Invoice)
        .where(Invoice.customer_id == customer.id)
        .order_by(Invoice.id)
    ).all()

    indexed = 0

    try:
        for invoice in invoices:
            index_invoice(db, invoice)
            invoice.indexing_status = "indexed"
            indexed += 1
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Indexing failed. Please retry later.",
        )

    return {
        "message": "Customer invoice reindex completed.",
        "indexed_invoices": indexed,
    }
