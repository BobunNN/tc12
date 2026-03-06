from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import SQLModel, Session, create_engine
from src.app.schemas.user import User
from src.app.config import get_settings


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            hashed_password="...",
            is_superuser=False,
        )
        session.add(user)
        session.commit()
        yield session


@pytest.fixture(autouse=True)
def mock_settings():
    mock = MagicMock()
    mock.SECRET_KEY = "test-secret"
    mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    mock.FIRST_SUPERUSER = "admin@test.com"
    mock.FIRST_SUPERUSER_PASSWORD = "password-test"
    mock.FIRST_SUPERUSER_FIRSTNAME = "Admin"
    mock.FIRST_SUPERUSER_LASTNAME = "User"

    with patch("src.app.core.security.get_settings", return_value=mock):
        get_settings.cache_clear()
        yield mock
        get_settings.cache_clear()
