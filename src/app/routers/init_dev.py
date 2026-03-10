from fastapi import APIRouter

from fastapi import APIRouter, Depends

from src.app.core.training_sessions import training_session_service
from src.app.dependencies import CurrentUser, SessionDep, get_current_active_superuser
from src.app.core.users import user_service

from src.app.schemas.training_sessions import TrainingSessions
from src.app.schemas.user import (
    UserCreate,
)
from datetime import time

router = APIRouter(tags=["test"])


@router.get("/init-test-users", tags=["test"])
def init_test_users(
    session: SessionDep,
):
    users = [
        UserCreate(
            first_name="user1",
            last_name="user1",
            email="user1@example.com",
            password="stringst",
        ),
        UserCreate(
            first_name="user2",
            last_name="user2",
            email="user2@example.com",
            password="stringst",
        ),
        UserCreate(
            first_name="user3",
            last_name="user3",
            email="user3@example.com",
            password="stringst",
        ),
        UserCreate(
            first_name="user4",
            last_name="user4",
            email="user4@example.com",
            password="stringst",
            is_trainer=True,
        ),
    ]

    for user_create in users:
        user_service.create_user(session=session, user_create=user_create)


@router.get("/init-training-session", tags=["test"])
def init_training_sessions(
    session: SessionDep,
):
    sessions = [
        TrainingSessions(
            id=0,
            day=1,
            trainer_id=1,
            session_start=time(10),
            session_duration=60,
            location="Carnot",
            court_number=1,
        ),
        TrainingSessions(
            id=1,
            day=1,
            trainer_id=1,
            session_start=time(13),
            session_duration=60,
            location="Carnot",
            court_number=2,
        ),
        TrainingSessions(
            id=2,
            day=1,
            trainer_id=5,
            session_start=time(10),
            session_duration=60,
            location="Leo Lagrange",
            court_number=1,
        ),
    ]

    for se in sessions:
        training_session_service.create_training_session(session, se)