
import secrets
import time

otp_store = {}

OTP_EXPIRY_SECONDS = 300
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5


def generate_otp(email: str) -> str:
    key = email.strip().lower()
    now = time.time()

    existing = otp_store.get(key)

    if existing:
        elapsed = now - existing["created_at"]

        if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
            raise ValueError("Please wait before requesting another OTP.")

    otp = f"{secrets.randbelow(1_000_000):06d}"

    otp_store[key] = {
        "otp": otp,
        "created_at": now,
        "expires_at": now + OTP_EXPIRY_SECONDS,
        "attempts": 0,
    }

    return otp


def verify_otp(email: str, otp: str) -> bool:
    key = email.strip().lower()
    record = otp_store.get(key)

    if not record:
        return False

    now = time.time()

    if now >= record["expires_at"]:
        otp_store.pop(key, None)
        return False

    if record["attempts"] >= OTP_MAX_ATTEMPTS:
        otp_store.pop(key, None)
        return False

    record["attempts"] += 1

    if secrets.compare_digest(record["otp"], otp):
        otp_store.pop(key, None)
        return True

    if record["attempts"] >= OTP_MAX_ATTEMPTS:
        otp_store.pop(key, None)

    return False
