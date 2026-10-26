
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    mobile_number: str = Field(
        pattern=r"^\+?[1-9]\d{7,14}$"
    )


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    mobile_number: str | None = None
    is_verified: bool


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str = Field(pattern=r"^\d{6}$")


class InvoiceCreate(BaseModel):
    invoice_number: str = Field(min_length=1, max_length=50)
    invoice_date: date
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )
    payment_status: Literal[
        "paid",
        "unpaid",
        "overdue",
    ] = "unpaid"


class InvoiceConfirmation(BaseModel):
    confirmed: bool
    invoice: InvoiceCreate
