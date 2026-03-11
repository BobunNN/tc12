class AbsenceNotFound(Exception): ...


class AbsenceAlreadyExists(Exception):
    """Raised when attempting to create an absence that already exists."""


class TraineeNotRegisteredForSession(Exception):
    """Raised when attempting to create an absence for a training session trainee is not attending."""


class TrainerDoesNotManageTrainingSession(Exception):
    """Raised when current user is a trainer attempting to create an absence for a trainee for a session the trainer is not managing."""


class AbsenceDateMismatchSessionDay(Exception):
    """Raised when trying to open an absence slot on the day not matching the corresponding session day"""
    
    
class AbsenceTraineeIdMismatch(Exception):
    """Raised when trainee tries to open an absence slot for somebody else than himself"""