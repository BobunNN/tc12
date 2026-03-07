from datetime import UTC, datetime
from typing import Literal

from pydantic import EmailStr, field_validator
from sqlmodel import AutoString, Field, SQLModel, DateTime
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserBase(SQLModel):
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)
    email: EmailStr = Field(max_length=30, unique=True, nullable=False)
    is_superuser: bool = False
    is_trainer: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class FrPhoneNumber(PhoneNumber):
    default_region_code = "FR"


class UserTennisInfo(SQLModel):
    gender: Literal["man", "woman"] | None = Field(default=None, sa_type=AutoString)
    birth_date: datetime | None = Field(default=None)
    looking_for_playmate: bool = Field(
        default=False, description="Player is looking for other tennis playmate"
    )
    tennis_availability: str | None = Field(
        default=None,
        description="Player looking for tennis playmate should add when they are available",
    )
    phone_number: FrPhoneNumber | None = Field(default=None)
    tennis_ranking: (
        Literal[
            "NC",
            "40",
            "30/5",
            "30/4",
            "30/3",
            "30/2",
            "30/1",
            "30",
            "15/5",
            "15/4",
            "15/3",
            "15/2",
            "15/1",
            "15",
            "5/6",
            "4/6",
            "3/6",
            "2/6",
            "1/6",
            "0",
        ]
        | None
    ) = Field(default=None, sa_type=AutoString)
    tennis_ranking_comment: str | None = Field(
        default=None,
        description="Mainly for unranked or players with decayed ranking",
        max_length=300,
    )

    @field_validator("birth_date", mode="before")
    def parse_birth_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%m/%Y")
        return value


class User(UserBase, UserTennisInfo, table=True):
    __tablename__ = "user_accounts"
    id: int | None = Field(default=None, primary_key=True, index=True, nullable=False)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class UserUpdate(UserBase, UserTennisInfo):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(UserTennisInfo):
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
