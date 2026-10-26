
"""add invoice embeddings

Revision ID: 729f1e7a6ff3
Revises: d7b1a131d754
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR


# revision identifiers, used by Alembic.
revision: str = "729f1e7a6ff3"
down_revision: Union[str, Sequence[str], None] = "d7b1a131d754"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invoice_embeddings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", VECTOR(768), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["invoice_id"],
            ["invoices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_id"),
    )

    op.create_index(
        op.f("ix_invoice_embeddings_customer_id"),
        "invoice_embeddings",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invoice_embeddings_id"),
        "invoice_embeddings",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invoice_embeddings_invoice_id"),
        "invoice_embeddings",
        ["invoice_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_invoice_embeddings_invoice_id"),
        table_name="invoice_embeddings",
    )
    op.drop_index(
        op.f("ix_invoice_embeddings_id"),
        table_name="invoice_embeddings",
    )
    op.drop_index(
        op.f("ix_invoice_embeddings_customer_id"),
        table_name="invoice_embeddings",
    )
    op.drop_table("invoice_embeddings")
