class SessionTraineeAssignementAlreadyExists(Exception):
    pass


class SessionTraineesLinkNotFound(Exception):
    pass


class SessionTraineesLinkInvalid(Exception):
    pass


class TraineesHasOverlappingSessions(Exception):
    pass


class TrainingSessionMaxCapacity(Exception):
    pass


class TraineeIsTrainer(Exception):
    """Raised when trying to assign a user that is a trainer to a session"""
