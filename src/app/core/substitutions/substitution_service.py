from datetime import UTC, datetime

from sqlmodel import Session

from src.app.core.absences.absence_service import AbsenceService
from src.app.core.substitutions.crud_substitutions import CrudSubstitutions
from src.app.core.substitutions.exceptions import (
    SubstitutionRequestAlreadyExists,
    SubstitutionRequestAlreadyReviewed,
    SubstitutionRequestNotFound,
    TrainerDoesNotManageSubstitutionSession,
)
from src.app.core.absences.exceptions import AbsenceNotFound
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
        self,
        session: Session,
        request_in: SubstitutionRequestCreate,
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

        absences = self.absence_service.get_absences_for_slot(
            session,
            training_session_id=request_in.session_id,
            absence_date=request_in.absence_date,
        )
        if not absences:
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
        current_user: User,
    ) -> SubstitutionRequests:
        request = self.get_substitution_request(session=session, request_id=request_id)

        if request.status != "pending":
            raise SubstitutionRequestAlreadyReviewed

        training_session = self.training_session_service.get_training_session(
            session=session, session_id=request.session_id
        )
        if training_session.trainer_id != current_user.id:
            raise TrainerDoesNotManageSubstitutionSession

        status = (
            request_update.status
            if isinstance(request_update, SubstitutionRequestUpdate)
            else request_update.get("status")
        )
        if status == "approved":
            absences = self.absence_service.get_absences_for_slot(
                session,
                training_session_id=request.session_id,
                absence_date=request.absence_date,
            )
            pending_absences = [a for a in absences if a.status == "pending"]
            if pending_absences:
                self.absence_service.confirm_absence(session, pending_absences[0])

            # Reject remaining pending sub requests only when all absences are now covered
            remaining_pending_absences = len(pending_absences) - 1
            if remaining_pending_absences <= 0:
                sibling_requests = self.crud_substitutions.get_with_filters(
                    session=session,
                    filters={
                        "session_id": request.session_id,
                        "absence_date": request.absence_date,
                    },
                )
                decline_update = SubstitutionRequestUpdate(
                    status="rejected", reviewed_at=datetime.now(UTC)
                )
                for sibling in sibling_requests:
                    if sibling.id != request_id and sibling.status == "pending":
                        self.crud_substitutions.update(
                            session=session, db_obj=sibling, obj_in=decline_update
                        )

        if isinstance(request_update, SubstitutionRequestUpdate):
            request_update.reviewed_at = datetime.now(UTC)
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
