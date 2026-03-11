from sqlmodel import Session

from src.app.core.users.crud_users import CRUDUsers
from src.app.schemas.user import User, UserCreate, UserUpdate

crud = CRUDUsers(User)


def test_create_user(session: Session):
    user_create = UserCreate(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        password="securepassword",
        is_superuser=False,
    )
    user = crud.create(session=session, obj_in=user_create)
    assert user.id is not None
    assert user.email == "alice@example.com"
    assert user.hashed_password != "securepassword"


def test_get_user_by_email(session: Session):
    user = crud.get_by_email(session=session, email="john@example.com")
    assert user is not None
    assert user.email == "john@example.com"


def test_get_user_by_id(session: Session):
    user = crud.get_by_email(session=session, email="john@example.com")
    found = crud.get_by_id(session=session, record_id=user.id)
    assert found is not None
    assert found.email == user.email


def test_get_all_users(session: Session):
    users = crud.get_all(session=session)
    assert isinstance(users, list)
    assert any(u.email == "john@example.com" for u in users)


def test_update_user(session: Session):
    user = crud.get_by_email(session=session, email="john@example.com")
    user_in = UserUpdate(first_name="Johnny")
    updated = crud.update(session=session, db_obj=user, obj_in=user_in)
    assert updated.first_name == "Johnny"
    assert updated.hashed_password  # unchanged, still hashed


def test_delete_user(session: Session):
    user_create = UserCreate(
        first_name="Bob",
        last_name="Brown",
        email="bob@example.com",
        password="anotherpassword",
        is_superuser=False,
    )
    crud.create(session=session, obj_in=user_create)
    deleted = crud.delete_by_email(session=session, email="bob@example.com")
    assert deleted is True
    gone = crud.get_by_email(session=session, email="bob@example.com")
    assert gone is None


def test_authenticate_user(session: Session):
    user_create = UserCreate(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        password="securepassword",
        is_superuser=False,
    )
    crud.create(session=session, obj_in=user_create)

    wrong_pwd = "wrong_pwd"
    password = "securepassword"

    assert (
        crud.authenticate(
            session=session, email="alice@example.com", password=wrong_pwd
        )
        is None
    )
    authd_user = crud.authenticate(
        session=session, email="alice@example.com", password=password
    )
    assert authd_user is not None
    assert authd_user.id is not None
    assert authd_user.email == "alice@example.com"
    assert authd_user.hashed_password != "securepassword"
