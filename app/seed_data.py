
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Customer, Invoice


SAMPLE_DATA = [
    {
        "name": "Arun",
        "email": "arun.demo@example.com",
        "invoices": [
            ("INV-101", date(2026, 10, 1), "2500.00", "unpaid"),
            ("INV-102", date(2026, 10, 3), "1800.00", "paid"),
            ("INV-103", date(2026, 10, 5), "3200.00", "overdue"),
            ("INV-104", date(2026, 10, 10), "950.00", "unpaid"),
            ("INV-105", date(2026, 10, 12), "4100.00", "paid"),
        ],
    },
    {
        "name": "Deepa",
        "email": "deepa.demo@example.com",
        "invoices": [
            ("INV-201", date(2026, 10, 2), "1500.00", "paid"),
            ("INV-202", date(2026, 10, 4), "2750.00", "unpaid"),
            ("INV-203", date(2026, 10, 6), "3600.00", "overdue"),
            ("INV-204", date(2026, 10, 11), "800.00", "unpaid"),
            ("INV-205", date(2026, 10, 13), "5200.00", "paid"),
        ],
    },
]


def seed_data():
    with SessionLocal() as db:
        for item in SAMPLE_DATA:
            customer = db.scalar(
                select(Customer).where(
                    Customer.email == item["email"]
                )
            )

            if customer is None:
                customer = Customer(
                    name=item["name"],
                    email=item["email"],
                    is_verified=False,
                )
                db.add(customer)
                db.flush()

            for number, invoice_date, amount, status in item["invoices"]:
                existing_invoice = db.scalar(
                    select(Invoice).where(
                        Invoice.customer_id == customer.id,
                        Invoice.invoice_number == number,
                    )
                )

                if existing_invoice is None:
                    db.add(
                        Invoice(
                            customer_id=customer.id,
                            invoice_number=number,
                            invoice_date=invoice_date,
                            amount=Decimal(amount),
                            currency="INR",
                            payment_status=status,
                        )
                    )

        db.commit()

    print("Sample customers and invoices seeded successfully.")


if __name__ == "__main__":
    seed_data()
