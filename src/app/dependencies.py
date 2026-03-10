from typing import Annotated, Generator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
import jwt
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import create_engine, Session

from src.app.core.security import ALGORITHM
from src.app.config import Settings, get_settings
from src.app.schemas.user import TokenPayload, User


sqlite_file_name = "app.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/login/token",
    scopes={
        "admin": "Admin rights",
        "user": "Read information about the current user.",
        "trainer": "Trainer scope",
    },
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


TokenDep = Annotated[str, Depends(oauth2_scheme)]
SessionDep = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_current_user(
    session: SessionDep,
    token: TokenDep,
    settings: SettingsDep,
    security_scopes: SecurityScopes,
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except InvalidTokenError, ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    if not token_data.sub or not token_data.sub.isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
        )

    user = session.get(User, int(token_data.sub))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

TrainerScope = Annotated[User, Security(get_current_user, scopes=["admin", "trainer"])]
