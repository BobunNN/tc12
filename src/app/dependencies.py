from typing import Annotated, Generator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
import jwt
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import NullPool
from sqlmodel import create_engine, Session

from src.app.core.security import ALGORITHM
from src.app.config import Settings, get_settings
from src.app.core.session_trainees_assignement.crud_session_trainees import (
    CRUDSessionTraineeAssignment,
)
from src.app.core.session_trainees_assignement.session_trainee_assignement_service import (
    SessionTraineeAssignementService,
)
from src.app.core.users.crud_users import CRUDUsers
from src.app.core.users.user_service import UserService
from src.app.schemas.user import TokenPayload, User
from src.app.core.absences.absence_service import AbsenceService
from src.app.core.training_sessions.training_session_service import (
    TrainingSessionService,
)
from src.app.core.training_sessions.crud_training_sessions import CRUDTrainingSessions
from src.app.core.absences.crud_absences import CrudAbsences
from src.app.schemas.training_sessions import (
    SessionTraineeAssignement,
    TrainingSessions,
)
from src.app.schemas.absences import Absences


sqlite_file_name = "app.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False, poolclass=NullPool)

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


def get_user_service() -> UserService:
    return UserService(crud_users=CRUDUsers(User))


def get_training_session_service() -> TrainingSessionService:
    return TrainingSessionService(
        crud_training_sessions=CRUDTrainingSessions(TrainingSessions),
        user_service=get_user_service(),
    )


def get_absence_service() -> AbsenceService:
    return AbsenceService(
        training_session_service=get_training_session_service(),
        session_trainee_link_service=get_session_trainee_assignement_service(),
        crud_absences=CrudAbsences(Absences),
    )


def get_session_trainee_assignement_service() -> SessionTraineeAssignementService:
    return SessionTraineeAssignementService(
        crud_session_trainees_link=CRUDSessionTraineeAssignment(
            SessionTraineeAssignement
        ),
        training_session_service=get_training_session_service(),
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AbsenceServiceDep = Annotated[AbsenceService, Depends(get_absence_service)]
TrainingSessionServiceDep = Annotated[
    TrainingSessionService, Depends(get_training_session_service)
]
SessionTraineeLinkServiceDep = Annotated[
    SessionTraineeAssignementService, Depends(get_session_trainee_assignement_service)
]
