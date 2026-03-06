import pytest
from unittest.mock import MagicMock, patch
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool  # <-- Add this import

from src.app.main import app
from src.app.dependencies import get_db
from src.app.config import get_settings
from src.app.schemas.user import User
from src.app.core.security import get_password_hash, create_access_token

# Update the engine to use StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # <-- Add this poolclass
)


@pytest.fixture(autouse=True)
def mock_settings():
    mock = MagicMock()
    mock.SECRET_KEY = "test-secret"
    mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    mock.FIRST_SUPERUSER = "admin@example.com"
    mock.FIRST_SUPERUSER_PASSWORD = "adminpass"
    mock.FIRST_SUPERUSER_FIRSTNAME = "Admin"
    mock.FIRST_SUPERUSER_LASTNAME = "User"

    with patch("src.app.core.security.get_settings", return_value=mock):
        get_settings.cache_clear()
        app.dependency_overrides[get_settings] = lambda: mock

        yield mock

        get_settings.cache_clear()
        app.dependency_overrides.pop(get_settings, None)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Add superuser
        superuser = User(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            hashed_password=get_password_hash("adminpass"),
            is_superuser=True,
        )
        session.add(superuser)

        # Add regular user
        regular = User(
            first_name="Regular",
            last_name="User",
            email="user@example.com",
            hashed_password=get_password_hash("userpass"),
            is_superuser=False,
        )
        session.add(regular)
        session.commit()

        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_db_override():
        yield session

    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(name="superuser_token_headers")
def superuser_token_headers_fixture():
    access_token = create_access_token(subject=1, expires_delta=timedelta(minutes=30))
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(name="normal_user_token_headers")
def normal_user_token_headers_fixture():
    access_token = create_access_token(subject=2, expires_delta=timedelta(minutes=30))
    return {"Authorization": f"Bearer {access_token}"}
