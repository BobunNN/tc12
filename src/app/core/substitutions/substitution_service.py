from typing import Sequence

from sqlmodel import Session, select
from src.app.core.substitutions.exceptions import (
    SubstitutionRequestAlreadyExists,
    SubstitutionRequestNotFound,
)
from src.app.core.substitutions import crud_substitutions
from src.app.schemas.substitution_requests import (
    SubstitutionRequests,
)
from src.app.schemas.user import (
    User,
)


def create_substitution_request(
    session: Session, request_create: SubstitutionRequests
) -> SubstitutionRequests:
    ...


def get_all_substitution_request(
    session: Session, offset, limit
) -> list[SubstitutionRequests]:
    return crud_substitutions.get_all_substitution_requests(
        session=session, offset=offset, limit=limit
    )


def get_substitution_request(session: Session, request_id: int) -> SubstitutionRequests:
    request_obj = crud_substitutions.get_substitution_request_by_id(session, request_id)
    if not request_obj:
        raise SubstitutionRequestNotFound
    return request_obj


def update_substitution_request(
    session: Session, db_request: SubstitutionRequests, request_update: dict
) -> SubstitutionRequests:
    return crud_substitutions.update_substitution_request(
        session, db_request, request_update
    )


def delete_substitution_request(session: Session, request_id: int) -> bool:
    return crud_substitutions.delete_substitution_request(session, request_id)


# def get_self_substitution_requests(
#     session: Session, current_user: User
# ) -> Sequence[SubstitutionRequests]:
#     if current_user.is_trainer:
#         statement = (
#             select(SubstitutionRequests)
#             .join(Absences, SubstitutionRequests.absence_id == Absences.id)
#             .join(TrainingSessions, Absences.training_session_id == TrainingSessions.id)
#             .where(TrainingSessions.trainer_id == current_user.id)
#         )
#         results = session.exec(statement).all()
#         return results
#     else:
#         return crud_substitutions.get_substitution_requests_with_filters(
#             session=session, filters={"requester_id": current_user.id}
#         )
