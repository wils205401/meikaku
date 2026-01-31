import jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from app.core.config import settings

from typing import Any

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(subject: str | Any) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"exp": expiry, "sub": str(subject)}

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt
