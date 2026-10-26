"""add invoice indexing status
Revision ID: 128b3ce23ad3
Revises: 02dd578b0b66
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = "128b3ce23ad3"
down_revision: Union[str, Sequence[str], None] = "02dd578b0b66"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    op.add_column(
        "invoices",
        sa.Column(
            "indexing_status",
            sa.String(length=20),
            server_default="pending_retry",
            nullable=False,
        ),
    )
def downgrade() -> None:
    op.drop_column("invoices", "indexing_status")
