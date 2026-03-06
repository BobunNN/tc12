from datetime import UTC, datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, DateTime


class UserBase(SQLModel):
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)
    email: EmailStr = Field(max_length=30, unique=True, nullable=False)
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class User(UserBase, table=True):
    __tablename__ = "user_accounts"
    id: int | None = Field(default=None, primary_key=True, index=True, nullable=False)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=30)
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None
