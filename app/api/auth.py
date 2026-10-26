
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_current_customer
from app.models import Customer
from app.schemas import CustomerCreate, CustomerResponse, OTPRequest, OTPVerify
from app.services.otp_service import generate_otp, verify_otp


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
OTP_DEV_FILE = os.getenv("OTP_DEV_FILE", ".dev_otp.txt")

router = APIRouter(prefix="/auth", tags=["Authentication"])


def create_access_token(customer_id: int) -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is missing from .env")

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(customer_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def deliver_development_otp(email: str, otp: str) -> None:
    """Store an OTP in a local development-only file."""
    if APP_ENV != "development":
        raise RuntimeError("Development OTP delivery is disabled.")

    project_root = Path.cwd().resolve()
    otp_path = (project_root / OTP_DEV_FILE).resolve()

    if otp_path.parent != project_root:
        raise RuntimeError(
            "OTP_DEV_FILE must be located in the project root."
        )

    with otp_path.open("a", encoding="utf-8") as file:
        file.write(
            f"Email: {email}\n"
            f"OTP: {otp}\n"
            f"Created: {datetime.now(timezone.utc).isoformat()}\n"
            "-------------------------\n"
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=CustomerResponse)
def register_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()
    mobile_number = data.mobile_number.strip()

    existing_email = db.scalar(
        select(Customer).where(Customer.email == email)
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    existing_mobile = db.scalar(
        select(Customer).where(
            Customer.mobile_number == mobile_number
        )
    )

    if existing_mobile:
        raise HTTPException(
            status_code=409,
            detail="Mobile number already registered",
        )

    customer = Customer(
        name=data.name.strip(),
        email=email,
        mobile_number=mobile_number,
    )

    try:
        db.add(customer)
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or mobile number already registered",
        )

    return customer


@router.post("/request-otp")
def request_otp(
    data: OTPRequest,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()

    customer = db.scalar(
        select(Customer).where(Customer.email == email)
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    if customer.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Customer is already verified",
        )

    if APP_ENV != "development":
        raise HTTPException(
            status_code=503,
            detail="OTP delivery provider is not configured.",
        )

    try:
        otp = generate_otp(email)
        deliver_development_otp(email, otp)
    except ValueError as exc:
        raise HTTPException(
            status_code=429,
            detail=str(exc),
        )
    except (OSError, RuntimeError):
        raise HTTPException(
            status_code=503,
            detail="Development OTP delivery is unavailable.",
        )

    return {
        "message": "OTP generated for development delivery.",
        "expires_in_seconds": 300,
    }


@router.post("/verify-otp")
def verify_customer_otp(
    data: OTPVerify,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()

    customer = db.scalar(
        select(Customer).where(Customer.email == email)
    )

    if not customer or not verify_otp(email, data.otp):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP",
        )

    try:
        access_token = create_access_token(customer.id)
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured.",
        )

    customer.is_verified = True
    db.commit()

    return {
        "message": "Email verified successfully",
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=CustomerResponse)
def get_my_profile(
    customer: Customer = Depends(get_current_customer),
):
    return customer

