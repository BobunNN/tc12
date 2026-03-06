from sqlmodel import Session
from src.app.schemas.user import UserCreate
from src.app.core.users import crud_users


def test_create_user(session: Session):
    user_create = UserCreate(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        password="securepassword",
        is_superuser=False,
    )
    user = crud_users.create_user(session=session, user_create=user_create)
    assert user.id is not None
    assert user.email == "alice@example.com"
    assert user.hashed_password != "securepassword"


def test_get_user_by_email(session: Session):
    user = crud_users.get_user_by_email(session=session, email="john@example.com")
    assert user is not None
    assert user.email == "john@example.com"


def test_get_user_by_id(session: Session):
    user = crud_users.get_user_by_email(session=session, email="john@example.com")
    found = crud_users.get_user_by_id(session=session, user_id=user.id)
    assert found is not None
    assert found.email == user.email


def test_get_all_users(session: Session):
    users = crud_users.get_all_users(session=session)
    assert isinstance(users, list)
    assert any(u.email == "john@example.com" for u in users)


def test_update_user(session: Session):
    user = crud_users.get_user_by_email(session=session, email="john@example.com")
    user_in = UserCreate(
        first_name="Johnny",
        last_name="Doe",
        email="john@example.com",
        password="newpassword",
        is_superuser=False,
    )
    updated = crud_users.update_user(session=session, db_user=user, user_in=user_in)
    assert updated.first_name == "Johnny"
    assert updated.hashed_password != "newpassword"


def test_delete_user(session: Session):
    user_create = UserCreate(
        first_name="Bob",
        last_name="Brown",
        email="bob@example.com",
        password="anotherpassword",
        is_superuser=False,
    )
    crud_users.create_user(session=session, user_create=user_create)
    crud_users.delete_user(session=session, email="bob@example.com")
    deleted = crud_users.get_user_by_email(session=session, email="bob@example.com")
    assert deleted is None


def test_authenticate_user(session: Session):
    user_create = UserCreate(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        password="securepassword",
        is_superuser=False,
    )
    crud_users.create_user(session=session, user_create=user_create)

    wrong_pwd = "wrong_pwd"
    password = "securepassword"

    assert (
        crud_users.authenticate_user(
            session=session, email="alice@example.com", password=wrong_pwd
        )
        is False
    )
    authd_user = crud_users.authenticate_user(
        session=session, email="alice@example.com", password=password
    )
    assert authd_user.id is not None
    assert authd_user.email == "alice@example.com"
    assert authd_user.hashed_password != "securepassword"
