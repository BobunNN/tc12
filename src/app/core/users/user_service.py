from typing import Any

from pydantic import EmailStr
from sqlmodel import Session
from fastapi import HTTPException
from src.app.core.security import get_password_hash, verify_password
from src.app.core.users.exceptions import (
    SelfDeleteNotAllowedHere,
    SuperUserSelfDeleteForbidden,
    UserAlreadyExists,
    UserNotFound,
)
from src.app.schemas.user import (
    UpdatePassword,
    User,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
)
from src.app.core.users import crud_users


def update_user_me(session: Session, user_in: UserUpdateMe, current_user: User) -> Any:
    if user_in.email:
        existing_user = crud_users.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != current_user.id:
            raise UserAlreadyExists
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


def update_password_me(
    session: Session, body: UpdatePassword, current_user: User
) -> Any:

    verified, _ = verify_password(body.current_password, current_user.hashed_password)
    if not verified:
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()


def get_all_users(session: Session, offset: int, limit: int) -> list[User]:
    return crud_users.get_all_users(session=session, offset=offset, limit=limit)


def get_user_by_email(session: Session, email: str) -> User:
    user = crud_users.get_user_by_email(session=session, email=email)
    if not user:
        raise UserNotFound
    return user


def create_user(session: Session, user_create: UserCreate) -> User:
    user = crud_users.get_user_by_email(session=session, email=user_create.email)
    if user:
        raise UserAlreadyExists
    user = crud_users.create_user(session=session, user_create=user_create)
    return user


def patch_user(session: Session, user_patch: UserUpdate, email: EmailStr) -> User:
    user = crud_users.get_user_by_email(session=session, email=email)
    if not user:
        raise UserNotFound
    user = crud_users.update_user(session=session, db_user=user, user_in=user_patch)
    return user


def delete_user(session: Session, email: EmailStr, current_user: User) -> Any:
    if current_user.email == email:
        raise SelfDeleteNotAllowedHere
    user = crud_users.get_user_by_email(session=session, email=email)
    if not user:
        raise UserNotFound
    crud_users.delete_user(session=session, email=email)
    return {"detail": "User deleted successfully."}


def delete_me(session, current_user: User) -> Any:
    if current_user.is_superuser:
        raise SuperUserSelfDeleteForbidden
    crud_users.delete_user(session=session, email=current_user.email)
    return {"detail": "User deleted successfully."}


def register_user(session: Session, user_in: UserRegister) -> User:
    user = crud_users.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise UserAlreadyExists
    user_create = UserCreate.model_validate(user_in)
    user = crud_users.create_user(session=session, user_create=user_create)
    return user


def check_is_trainer(session: Session, id: int) -> bool:
    user = crud_users.get_user_by_id(session=session, user_id=id)
    if not user:
        raise UserNotFound
    return user.is_trainer
