from datetime import date
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    mobile_number: Mapped[str | None] = mapped_column(
        String(15),
        unique=True,
        index=True,
        nullable=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200), default="New conversation", nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="conversations"
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages"
    )


class Invoice(Base):
    __tablename__ = "invoices"

    __table_args__ = (
        UniqueConstraint(
            "customer_id",
            "invoice_number",
            name="uq_invoice_customer_number",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_invoice_amount_positive",
        ),
        CheckConstraint(
            "payment_status IN ('paid', 'unpaid', 'overdue')",
            name="ck_invoice_payment_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invoice_number: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    invoice_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3), default="INR", nullable=False
    )
    payment_status: Mapped[str] = mapped_column(
        String(20), default="unpaid", nullable=False
    )
    indexing_status: Mapped[str] = mapped_column(
        String(20), default="pending_retry",
        server_default="pending_retry", nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="invoices"
    )


class InvoiceEmbedding(Base):
    __tablename__ = "invoice_embeddings"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    embedding: Mapped[list[float]] = mapped_column(
        Vector(768), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

