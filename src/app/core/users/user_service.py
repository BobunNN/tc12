from typing import Any

from pydantic import EmailStr
from sqlmodel import Session
from src.app.core.security import get_password_hash, verify_password
from src.app.core.users.exceptions import (
    IncorrectPassword,
    NewPasswordCannotBeTheSameAsTheCurrentOne,
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
from src.app.core.users.crud_users import CRUDUsers


class UserService:
    def __init__(self, crud_users: CRUDUsers) -> None:
        self.crud_users = crud_users

    def update_user_me(
        self, session: Session, user_in: UserUpdateMe, current_user: User
    ) -> Any:
        if user_in.email:
            existing_user = self.crud_users.get_by_email(
                session=session, email=user_in.email
            )
            if existing_user and existing_user.id != current_user.id:
                raise UserAlreadyExists
        return self.crud_users.update(session, current_user, user_in)

    def update_password_me(
        self, session: Session, body: UpdatePassword, current_user: User
    ) -> Any:

        verified, _ = verify_password(
            body.current_password, current_user.hashed_password
        )
        if not verified:
            raise IncorrectPassword
        if body.current_password == body.new_password:
            raise NewPasswordCannotBeTheSameAsTheCurrentOne
        hashed_password = get_password_hash(body.new_password)
        return self.crud_users.update(
            session, current_user, {"hashed_password": hashed_password}
        )

    def get_all_users(self, session: Session, offset: int, limit: int) -> list[User]:
        return self.crud_users.get_all(session=session, offset=offset, limit=limit)

    def get_user_by_email(self, session: Session, email: str) -> User:
        user = self.crud_users.get_by_email(session=session, email=email)
        if not user:
            raise UserNotFound
        return user

    def create_user(self, session: Session, user_create: UserCreate) -> User:
        user = self.crud_users.get_by_email(session=session, email=user_create.email)
        if user:
            raise UserAlreadyExists
        user = self.crud_users.create(session=session, obj_in=user_create)
        return user

    def patch_user(
        self, session: Session, user_patch: UserUpdate, email: EmailStr
    ) -> User:
        user = self.crud_users.get_by_email(session=session, email=email)
        if not user:
            raise UserNotFound
        user = self.crud_users.update(session=session, db_obj=user, obj_in=user_patch)
        return user

    def delete_user(self, session: Session, email: EmailStr, current_user: User) -> Any:
        if current_user.email == email:
            raise SelfDeleteNotAllowedHere
        user = self.crud_users.get_by_email(session=session, email=email)
        if not user:
            raise UserNotFound
        self.crud_users.delete_by_email(session=session, email=email)
        return {"detail": "User deleted successfully."}

    def delete_me(self, session: Session, current_user: User) -> Any:
        if current_user.is_superuser:
            raise SuperUserSelfDeleteForbidden
        self.crud_users.delete_by_email(session=session, email=current_user.email)
        return {"detail": "User deleted successfully."}

    def register_user(self, session: Session, user_in: UserRegister) -> User:
        user = self.crud_users.get_by_email(session=session, email=user_in.email)
        if user:
            raise UserAlreadyExists
        user_create = UserCreate.model_validate(user_in)
        user = self.crud_users.create(session=session, obj_in=user_create)
        return user

    def check_is_trainer(self, session: Session, id: int) -> bool:
        user: User | None = self.crud_users.get_by_id(session=session, record_id=id)
        if not user:
            raise UserNotFound
        return user.is_trainer
