
import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Customer

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

bearer_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Customer:
    if not JWT_SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="JWT configuration is missing",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        customer_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    customer = db.scalar(
        select(Customer).where(Customer.id == customer_id)
    )

    if not customer or not customer.is_verified:
        raise HTTPException(
            status_code=401,
            detail="Verified customer not found",
        )

    return customer
