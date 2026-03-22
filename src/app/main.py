import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # noqa
from src.app.routers import (
    bulk_load,
    session_trainee_assignment,
    substitutions,
    training_sessions,
    users,
    login,
    exceptions_manager,
    absences,
    init_dev,
)

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exceptions_manager.register_exception_handlers(app)

app.include_router(users.router)
app.include_router(login.router)
app.include_router(substitutions.router)
app.include_router(training_sessions.router)
app.include_router(absences.router)
app.include_router(init_dev.router)
app.include_router(session_trainee_assignment.router)
app.include_router(bulk_load.router)


@app.get(
    "/",
)
def root() -> str:
    logging.info("Health check endpoint called.")
    return "ok"
