from src.app.schemas.absences import AbsenceUpdate, Absences, AbsenceCreate
from src.app.core.crud.crud_base import CRUDBase


class CrudAbsences(CRUDBase[Absences, AbsenceCreate, AbsenceUpdate]):
    pass
