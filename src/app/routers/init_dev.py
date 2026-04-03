from fastapi import APIRouter

from src.app.dependencies import (
    SessionDep,
    SessionTraineeLinkServiceDep,
    TrainingSessionServiceDep,
    UserServiceDep,
)

from src.app.schemas.training_sessions import TrainingSessionCreate
from src.app.schemas.user import (
    UserCreate,
)
from datetime import time

router = APIRouter(tags=["test"])


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

sessions = [
    TrainingSessionCreate(
        day="1",
        trainer_id=1,
        session_start=time(10),
        session_duration=60,
        location="Carnot",
        court_number=1,
    ),
    TrainingSessionCreate(
        day="1",
        trainer_id=1,
        session_start=time(13),
        session_duration=60,
        location="Carnot",
        court_number=2,
    ),
    TrainingSessionCreate(
        day="1",
        trainer_id=5,
        session_start=time(10),
        session_duration=60,
        location="Leo Lagrange",
        court_number=1,
    ),
    TrainingSessionCreate(
        day="2",
        trainer_id=5,
        session_start=time(10),
        session_duration=60,
        location="Leo Lagrange",
        court_number=1,
    ),
]


@router.get("/init-test-users", tags=["test"])
def init_test_users(
    session: SessionDep,
    user_service: UserServiceDep,
):
    for user_create in users:
        user_service.create_user(session=session, user_create=user_create)


@router.get("/init-training-session", tags=["test"])
def init_training_sessions(
    session: SessionDep, training_session_service: TrainingSessionServiceDep
):

    for se in sessions:
        training_session_service.create_training_session(session, se)


@router.get("/init-trainees-assignment", tags=["test"])
def init_trainees(
    session: SessionDep,
    session_assignment_service: SessionTraineeLinkServiceDep,
):
    sessions_trainees = [(2, 1), (3, 1), (2, 4)]
    for se in sessions_trainees:
        session_assignment_service.create_session_trainees_link(session, se[0], se[1])
