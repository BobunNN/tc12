from pydantic import EmailStr
from sqlmodel import Session

from src.app.core.crud.crud_base import CRUDBase
from src.app.core.security import DUMMY_HASH, get_password_hash, verify_password
from src.app.schemas.user import User, UserCreate, UserUpdate


class CRUDUsers(CRUDBase[User, UserCreate, UserUpdate]):
    """
    get_by_id, get_all, get_with_filters, create, update, delete_by_id
    are all inherited.

    Bespoke methods cover email-based lookup and password authentication,
    which are domain-specific and don't belong in the generic base.
    """

    def get_by_email(self, session: Session, email: str) -> User | None:
        return self.get_by_composite_key(session, email=email)

    # type: ignore[override]
    def create(self, session: Session, obj_in: UserCreate) -> User:
        """Overrides base create to hash the password before persisting."""
        db_obj = User.model_validate(
            obj_in, update={"hashed_password": get_password_hash(obj_in.password)}
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete_by_email(self, session: Session, email: EmailStr) -> bool:
        return self.delete_by_composite_key(session, email=email)

    def authenticate(self, session: Session, email: str, password: str) -> User | None:
        """Returns the User on success, None on failure."""
        user = self.get_by_email(session, email)
        if not user:
            verify_password(password, DUMMY_HASH)  # constant-time dummy check
            return None
        verified, updated_hash = verify_password(password, user.hashed_password)
        if not verified:
            return None
        if updated_hash:
            user.hashed_password = updated_hash
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
