from typing import Any

from pydantic import EmailStr
from sqlmodel import Session, select

from src.app.core.security import DUMMY_HASH, get_password_hash, verify_password
from src.app.schemas.user import User, UserCreate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create a new user in the database.
    Hashes the password before saving.
    Returns the created User object.
    """
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserCreate) -> Any:
    """
    Update an existing user in the database.
    If a new password is provided, it will be hashed and updated.
    Returns the updated User object.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Retrieve a user from the database by their email address.
    Returns the User object if found, else None.
    """
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def get_user_by_id(*, session: Session, user_id: int) -> User | None:
    """
    Retrieve a user from the database by their user ID.
    Returns the User object if found, else None.
    """
    statement = select(User).where(User.id == user_id)
    session_user = session.exec(statement).first()
    return session_user


def authenticate_user(*, session: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.
    Returns the User object if authentication is successful, else False.
    Updates the password hash if needed.
    """
    user = get_user_by_email(session=session, email=email)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    verified, updated_password_hash = verify_password(password, user.hashed_password)
    if not verified:
        return False
    if updated_password_hash:
        user.hashed_password = updated_password_hash
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def get_all_users(*, session: Session, offset: int = 0, limit: int = 100) -> list[User]:
    """
    Retrieve all users from the database with pagination support.
    Returns a list of User objects.
    """
    statement = select(User).offset(offset).limit(limit)
    users = session.exec(statement).all()
    return users


def delete_user(*, session: Session, email: EmailStr) -> bool:
    """
    Delete a user from the database by their email address.
    Returns True if deletion is successful.
    """
    user = get_user_by_email(session=session, email=email)
    session.delete(user)
    session.commit()
