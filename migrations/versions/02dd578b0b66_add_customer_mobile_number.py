
"""add customer mobile number

Revision ID: 02dd578b0b66
Revises: 729f1e7a6ff3
Create Date: 2026-10-23 18:40:59.335174
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "02dd578b0b66"
down_revision: Union[str, Sequence[str], None] = "729f1e7a6ff3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column("mobile_number", sa.String(length=15), nullable=True),
    )
    op.create_index(
        op.f("ix_customers_mobile_number"),
        "customers",
        ["mobile_number"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_customers_mobile_number"),
        table_name="customers",
    )
    op.drop_column("customers", "mobile_number")
