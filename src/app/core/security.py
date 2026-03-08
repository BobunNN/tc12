from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from pwdlib import PasswordHash
from src.app.config import get_settings


ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")


def create_access_token(data: dict | Any, expires_delta: timedelta) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(plain_password, hashed_password):
    return password_hash.verify_and_update(plain_password, hashed_password)
