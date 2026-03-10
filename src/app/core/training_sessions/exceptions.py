class TrainingSessionAlreadyExists(Exception):
    """Raised when attempting to create a training session that already exists."""
    ...

class TrainingSessionNotFound(Exception):
    """Raised when a training session cannot be found in the database."""
    ...

    
class TrainingSessionOverlap(Exception):
    """Raised when a training session trying to be created overlap with an existing training session"""
    

class TrainingSessionInvalidTrainer(Exception):
    """Raised when trying to create a training session with a non trainer"""
    
    
class TrainingSessionInvalidLocation(Exception):
    """Raised when trying to create a training session with a non trainer"""