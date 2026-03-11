from typing import Any, Generic, TypeVar, Type

from pydantic import BaseModel
from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel | BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel | BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD base class providing reusable database operations for SQLModel models.

    Supports:
        - Single primary key lookups (e.g. User, TrainingSessions)
        - Composite primary key lookups (e.g. Absences: trainee_id + training_session_id + absence_date)
        - Filter-based queries
        - Standard create / update / delete operations

    Type Parameters:
        ModelType:        The SQLModel table model (e.g. User, Absences, TrainingSessions).
        CreateSchemaType: The Pydantic/SQLModel schema used for creation.
        UpdateSchemaType: The Pydantic/SQLModel schema used for updates.

    Usage:
        # Single-PK model
        class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
            pass

        crud_user = CRUDUser(User)

        # Composite-PK model
        class CRUDAbsence(CRUDBase[Absences, AbsenceCreate, AbsenceUpdate]):
            pass

        crud_absence = CRUDAbsence(Absences)
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, session: Session, record_id: Any) -> ModelType | None:
        """
        Fetch a single record by its primary key value.

        Works for single-column integer PKs (e.g. User.id, TrainingSessions.id).
        For composite PKs use get_by_composite_key() instead.

        Args:
            session:   Active SQLModel/SQLAlchemy session.
            record_id: The primary key value (e.g. an int or UUID).

        Returns:
            The matching model instance, or None if not found.

        Example:
            user = crud_user.get_by_id(session, 42)
        """
        return session.get(self.model, record_id)

    def get_by_composite_key(
        self, session: Session, **key_fields: Any
    ) -> ModelType | None:
        """
        Fetch a single record identified by a composite primary key.

        Each keyword argument must match a column name on the model.

        Args:
            session:    Active SQLModel/SQLAlchemy session.
            **key_fields: Composite key columns and their values.

        Returns:
            The matching model instance, or None if not found.

        Example:
            absence = crud_absence.get_by_composite_key(
                session,
                trainee_id=3,
                training_session_id=1,
                absence_date=datetime(2026, 3, 17),
            )
        """
        statement = select(self.model)
        for field, value in key_fields.items():
            col = getattr(self.model, field, None)
            if col is None:
                raise AttributeError(
                    f"Model '{self.model.__name__}' has no attribute '{field}'."
                )
            statement = statement.where(col == value)
        return session.exec(statement).first()

    def get_all(
        self, session: Session, offset: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """
        Fetch a paginated list of all records.

        Args:
            session: Active SQLModel/SQLAlchemy session.
            offset:  Number of records to skip (default 0).
            limit:   Maximum records to return (default 100).

        Returns:
            List of model instances.

        Example:
            all_sessions = crud_training_session.get_all(session, offset=0, limit=50)
        """
        statement = select(self.model).offset(offset).limit(limit)
        return list(session.exec(statement).all())

    def get_with_filters(
        self,
        session: Session,
        filters: dict[str, Any],
        offset: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """
        Fetch records matching all supplied exact-match filters.

        Only filters whose key corresponds to a real column on the model are applied;
        unrecognised keys are silently ignored to stay consistent with the
        existing module behaviour.

        Args:
            session: Active SQLModel/SQLAlchemy session.
            filters: Mapping of column name → value to filter by.
                     Example: {"trainee_id": 3, "status": "pending"}
            offset:  Number of records to skip (default 0).
            limit:   Maximum records to return (default 100).

        Returns:
            List of matching model instances.

        Example:
            absences = crud_absence.get_with_filters(
                session, {"trainee_id": 3, "status": "pending"}
            )
        """
        statement = select(self.model)
        for key, value in filters.items():
            col = getattr(self.model, key, None)
            if col is not None:
                statement = statement.where(col == value)
        statement = statement.offset(offset).limit(limit)
        return list(session.exec(statement).all())

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, session: Session, obj_in: CreateSchemaType) -> ModelType:
        """
        Persist a new record derived from a creation schema.

        The creation schema is validated and coerced into the table model via
        SQLModel's model_validate(), so all default values and validators run.

        Args:
            session: Active SQLModel/SQLAlchemy session.
            obj_in:  Validated creation schema instance.

        Returns:
            The newly created, db-refreshed model instance.

        Example:
            new_session = crud_training_session.create(session, session_create)
        """
        db_obj = self.model.model_validate(obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """
        Apply a partial or full update to an existing record.

        Accepts either an update schema (only fields explicitly set are applied,
        via model_dump(exclude_unset=True)) or a plain dict.

        Args:
            session: Active SQLModel/SQLAlchemy session.
            db_obj:  The existing model instance to update (fetched beforehand).
            obj_in:  Update schema instance or dict of fields to change.

        Returns:
            The updated, db-refreshed model instance.

        Example:
            updated = crud_training_session.update(
                session, db_session, TrainingSessionUpdate(court_number=3)
            )
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete_by_id(self, session: Session, record_id: Any) -> bool:
        """
        Delete a record by its single primary key value.

        Args:
            session:   Active SQLModel/SQLAlchemy session.
            record_id: The primary key value.

        Returns:
            True if the record existed and was deleted, False otherwise.

        Example:
            deleted = crud_training_session.delete_by_id(session, 7)
        """
        db_obj = self.get_by_id(session, record_id)
        if db_obj is None:
            return False
        session.delete(db_obj)
        session.commit()
        return True

    def delete_by_composite_key(self, session: Session, **key_fields: Any) -> bool:
        """
        Delete a record identified by a composite primary key.

        Args:
            session:      Active SQLModel/SQLAlchemy session.
            **key_fields: Composite key columns and their values.

        Returns:
            True if the record existed and was deleted, False otherwise.

        Example:
            deleted = crud_absence.delete_by_composite_key(
                session,
                trainee_id=3,
                training_session_id=1,
                absence_date=datetime(2026, 3, 17),
            )
        """
        db_obj = self.get_by_composite_key(session, **key_fields)
        if db_obj is None:
            return False
        session.delete(db_obj)
        session.commit()
        return True
