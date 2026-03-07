import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # noqa
<<<<<<< HEAD
from src.app.routers import (
    substitutions,
    training_sessions,
    users,
    login,
    exceptions_manager,
)
=======
from src.app.routers import users, login, exceptions_manager
>>>>>>> main

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI()

# Optional: Enable CORS (uncomment to use)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust as needed
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

exceptions_manager.register_exception_handlers(app)

app.include_router(users.router)
app.include_router(login.router)
<<<<<<< HEAD
app.include_router(substitutions.router)
app.include_router(training_sessions.router)
=======
>>>>>>> main


@app.get(
    "/",
)
def root() -> str:
    logging.info("Health check endpoint called.")
    return "ok"
