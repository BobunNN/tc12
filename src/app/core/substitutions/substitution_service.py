from datetime import UTC, datetime

from sqlmodel import Session

from src.app.core.absences.absence_service import AbsenceService
from src.app.core.substitutions.crud_substitutions import CrudSubstitutions
from src.app.core.substitutions.exceptions import (
    SubstitutionRequestAlreadyExists,
    SubstitutionRequestNotFound,
)
from src.app.core.training_sessions.training_session_service import (
    TrainingSessionService,
)
from src.app.schemas.substitution_requests import (
    SubstitutionRequestCreate,
    SubstitutionRequestUpdate,
    SubstitutionRequests,
)
from src.app.schemas.user import User


class SubstitutionService:
    def __init__(
        self,
        crud_substitutions: CrudSubstitutions,
        training_session_service: TrainingSessionService,
        absence_service: AbsenceService,
    ) -> None:
        self.crud_substitutions = crud_substitutions
        self.training_session_service = training_session_service
        self.absence_service = absence_service

    def create_substitution_request(
        self, session: Session, request_in: SubstitutionRequestCreate
    ) -> SubstitutionRequests:
        # Check for existing substitution request
        existing = self.crud_substitutions.get_by_composite_key(
            session,
            session_id=request_in.session_id,
            absence_date=request_in.absence_date,
            requester_id=request_in.requester_id,
        )
        if existing:
            raise SubstitutionRequestAlreadyExists

        # Check for corresponding absence
        absence = self.absence_service.search_unique_absence(
            session,
            trainee_id=request_in.requester_id,
            training_session_id=request_in.session_id,
            absence_date=request_in.absence_date,
        )
        if not absence:
            from src.app.core.absences.exceptions import AbsenceNotFound

            raise AbsenceNotFound

        now = datetime.now(UTC)
        create_data = SubstitutionRequestCreate(
            session_id=request_in.session_id,
            absence_date=request_in.absence_date,
            requester_id=request_in.requester_id,
            status=request_in.status,
            created_at=now,
            reviewed_at=now,
        )
        return self.crud_substitutions.create(session=session, obj_in=create_data)

    def get_substitution_request(
        self, session: Session, request_id: int
    ) -> SubstitutionRequests:
        request = self.crud_substitutions.get_by_id(
            session=session, record_id=request_id
        )
        if not request:
            raise SubstitutionRequestNotFound
        return request

    def get_all_substitution_request(
        self, session: Session, limit: int, offset: int
    ) -> list[SubstitutionRequests]:
        return self.crud_substitutions.get_all(
            session=session, offset=offset, limit=limit
        )

    def get_self_substitution_requests(
        self, session: Session, current_user: User
    ) -> list[SubstitutionRequests]:
        if current_user.is_trainer:
            trainer_sessions = self.training_session_service.search_training_session(
                session=session, filters={"trainer_id": current_user.id}
            )
            session_ids = [ts.id for ts in trainer_sessions]
            if not session_ids:
                return []
            all_requests: list[SubstitutionRequests] = []
            for session_id in session_ids:
                requests = self.crud_substitutions.get_with_filters(
                    session=session, filters={"session_id": session_id}
                )
                all_requests.extend(requests)
            return all_requests
        return self.crud_substitutions.get_with_filters(
            session=session, filters={"requester_id": current_user.id}
        )

    def update_substitution_request(
        self,
        session: Session,
        request_id: int,
        request_update: SubstitutionRequestUpdate | dict,
    ) -> SubstitutionRequests:
        request = self.get_substitution_request(session=session, request_id=request_id)
        return self.crud_substitutions.update(
            session=session, db_obj=request, obj_in=request_update
        )

    def delete_substitution_request(
        self, session: Session, request_id: int, current_user: User
    ) -> None:
        request = self.get_substitution_request(session=session, request_id=request_id)
        if request.requester_id != current_user.id and not current_user.is_superuser:
            raise SubstitutionRequestNotFound
        self.crud_substitutions.delete_by_id(session=session, record_id=request_id)
