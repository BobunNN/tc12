from sqlmodel import Session, select
from src.app.schemas.training_sessions import TrainingSessions, Absences


# CRUD for TrainingSessions
def create_training_session(
    session: Session, session_create: TrainingSessions
) -> TrainingSessions:
    db_obj = TrainingSessions.model_validate(session_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_training_session_by_id(
    session: Session, session_id: int
) -> TrainingSessions | None:
    statement = select(TrainingSessions).where(TrainingSessions.id == session_id)
    return session.exec(statement).first()


def get_all_training_sessions(
    session: Session, offset: int = 0, limit: int = 100
) -> list[TrainingSessions]:
    statement = select(TrainingSessions).offset(offset).limit(limit)
    return session.exec(statement).all()


def update_training_session(
    session: Session, db_session: TrainingSessions, session_update: dict
) -> TrainingSessions:
    db_session.sqlmodel_update(session_update)
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session


def delete_training_session(session: Session, session_id: int) -> bool:
    db_session = get_training_session_by_id(session, session_id)
    if db_session:
        session.delete(db_session)
        session.commit()
        return True
    return False


# CRUD for Absences
def create_absence(session: Session, absence_create: Absences) -> Absences:
    db_obj = Absences.model_validate(absence_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_absence_by_id(session: Session, absence_id: int) -> Absences | None:
    statement = select(Absences).where(Absences.id == absence_id)
    return session.exec(statement).first()


def get_all_absences(
    session: Session, offset: int = 0, limit: int = 100
) -> list[Absences]:
    statement = select(Absences).offset(offset).limit(limit)
    return session.exec(statement).all()


def update_absence(
    session: Session, db_absence: Absences, absence_update: dict
) -> Absences:
    db_absence.sqlmodel_update(absence_update)
    session.add(db_absence)
    session.commit()
    session.refresh(db_absence)
    return db_absence


def delete_absence(session: Session, absence_id: int) -> bool:
    db_absence = get_absence_by_id(session, absence_id)
    if db_absence:
        session.delete(db_absence)
        session.commit()
        return True
    return False
