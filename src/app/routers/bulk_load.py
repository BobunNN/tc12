import csv
import io
import urllib.parse
from fastapi import APIRouter, HTTPException, Security, UploadFile, status

from src.app.dependencies import (
    SessionDep,
    SessionTraineeLinkServiceDep,
    TrainingSessionServiceDep,
    UserServiceDep,
    get_current_user,
)
from src.app.schemas.training_sessions import TrainingSessionCreate
from src.app.schemas.user import UserCreate


router = APIRouter(prefix="/bulk-load")


@router.post(
    "/users",
    dependencies=[Security(get_current_user, scopes=["trainer", "admin"])],
)
async def load_users(
    session: SessionDep,
    file: UploadFile,
    user_service: UserServiceDep,
):
    data = await read_input_file(file)
    csv_reader = csv.DictReader(io.StringIO(data))
    headers = csv_reader.fieldnames
    if headers != ["first_name", "last_name", "is_trainer"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid file format - should be 'first_name','last_name','is_trainer'",
        )

    for row in csv_reader:
        new_user = UserCreate(
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=f"{urllib.parse.quote(row['first_name'])}.{urllib.parse.quote(row['last_name'])}@example.com",  # TODO temporary for dev
            is_trainer=True if row["is_trainer"] == "1" else False,
            password="stringst",
        )
        user_service.create_user(session=session, user_create=new_user)
    return "ok"


@router.post(
    "/training_sessions",
    dependencies=[Security(get_current_user, scopes=["trainer", "admin"])],
)
async def load_training_sessions(
    session: SessionDep,
    file: UploadFile,
    training_session_service: TrainingSessionServiceDep,
):
    data = await read_input_file(file)
    csv_reader = csv.DictReader(io.StringIO(data))
    headers = csv_reader.fieldnames
    if headers != [
        "trainer_id",
        "location",
        "court_number",
        "session_start",
        "session_duration",
        "day",
    ]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid file format - should be 'trainer_id','location','court_number','session_start','session_duration','day'",
        )

    for new_session in csv_reader:
        session_create = TrainingSessionCreate.model_validate(new_session)
        training_session_service.create_training_session(session, session_create)

    return "ok"


@router.post(
    "/assignments",
    dependencies=[Security(get_current_user, scopes=["trainer", "admin"])],
)
async def load_assignments(
    session: SessionDep,
    file: UploadFile,
    session_trainee_link_service: SessionTraineeLinkServiceDep,
):
    data = await read_input_file(file)
    csv_reader = csv.DictReader(io.StringIO(data))
    headers = csv_reader.fieldnames
    if headers != ["session_id", "member_id"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid file format - should be 'session_id', 'member_id'",
        )

    for row in csv_reader:
        session_trainee_link_service.create_session_trainees_link(
            session=session, session_id=row["session_id"], trainee_id=row["member_id"]
        )

    return "ok"


async def read_input_file(file: UploadFile):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="File must be a CSV",
        )

    contents = await file.read()

    try:
        decoded_contents = contents.decode("utf-8")
        return decoded_contents
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid file encoding. Must be UTF-8.",
        )
