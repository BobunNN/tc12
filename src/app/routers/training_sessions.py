from fastapi import APIRouter, Depends, Security
from src.app.dependencies import CurrentUser, SessionDep, get_current_user
from src.app.schemas.training_sessions import TrainingSessions, TrainingSessionsUpdate
from src.app.core.training_sessions import (
    training_session_service,
)

router = APIRouter(tags=["training_sessions"])


@router.post(
    "/v1/training-sessions",
    dependencies=[Security(get_current_user, scopes=["trainer"])],
)
def create_training_session(
    session: SessionDep,
    session_create: TrainingSessions,
):
    return training_session_service.create_training_session(
        session=session, session_create=session_create
    )


@router.get(
    "/v1/training-sessions/session-trainees", dependencies=[Depends(get_current_user)]
)
def get_session_trainee(
    session: SessionDep,
    session_id: int,
):
    return training_session_service.search_session_trainees(session, session_id)


@router.get("/v1/training-sessions/me", dependencies=[Depends(get_current_user)])
def get_self_training_session(
    session: SessionDep,
    current_user: CurrentUser,
):
    return training_session_service.get_self_training_session(
        session=session, user=current_user
    )


@router.get(
    "/v1/training-sessions/{session_id}", dependencies=[Depends(get_current_user)]
)
def get_training_session(
    session: SessionDep,
    session_id: int,
):
    return training_session_service.get_training_session(session, session_id)


@router.get("/v1/training-sessions", dependencies=[Depends(get_current_user)])
def get_all_training_sessions(session: SessionDep, offset: int = 0, limit: int = 100):
    return training_session_service.get_all_training_sessions(session, offset, limit)


@router.patch(
    "/v1/training-sessions/{session_id}",
    dependencies=[Security(get_current_user, scopes=["trainer"])],
)
def update_training_session(
    session: SessionDep,
    session_id: int,
    session_update: TrainingSessionsUpdate,
):
    return training_session_service.update_training_session(
        session=session, session_id=session_id, session_update=session_update
    )


@router.delete(
    "/v1/training-sessions/{session_id}",
    dependencies=[Security(get_current_user, scopes=["trainer"])],
)
def delete_training_session(
    session: SessionDep,
    session_id: int,
):
    return training_session_service.remove_training_session(session, session_id)


@router.post("/v1/training-sessions/trainee-assignement")
def assign_trainee_to_session(session: SessionDep, session_id: int, trainee_id: int):
    return training_session_service.assign_trainee_session(
        session=session, trainee_id=trainee_id, session_id=session_id
    )


# TODO move to batch resources
# @router.post(
#     "/v1/training-sessions-batch",
#     dependencies=[Security(get_current_user, scopes=["trainer"])],
# )
# async def create_training_sessions_bulk(
#     session: SessionDep, training_schedule_csv: UploadFile
# ):
#     """_summary_

#     Args:
#         session (SessionDep): _description_
#         training_schedule_csv (UploadFile): _description_

#     Raises:
#         HTTPException: _description_
#         HTTPException: _description_

#     Returns:
#         _type_: _description_
#     """
#     if not training_schedule_csv.filename.endswith(".csv"):
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
#             detail="File must be a CSV",
#         )

#     contents = await training_schedule_csv.read()

#     try:
#         decoded_contents = contents.decode("utf-8")
#     except UnicodeDecodeError:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
#             detail="Invalid file encoding. Must be UTF-8.",
#         )

#     csv_reader = csv.DictReader(io.StringIO(decoded_contents))

#     parsed_records = list(csv_reader)

#     return training_session_service.bulk_load_training_sessions(
#         session=session, records=parsed_records
#     )
