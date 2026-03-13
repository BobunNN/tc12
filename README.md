# 📝 App Overview

This API manages a tennis club's core operations:

- **Users:** Trainers and trainees, each with roles and permissions.
- **Training Sessions:** Scheduled by trainers, with day, time, location, and court.
- **Session Assignments:** Trainees are assigned to sessions; trainers manage their own sessions.
- **Absences:** Trainees (or trainers on their behalf) can report absences for specific sessions and dates.

The API is modular, with clear separation between routing, business logic, and data models.

---

## 🔒 Business Rules & Constraints

- **User Roles:**
	- Trainers can only manage sessions they are assigned to.
	- Trainees can only report absences for sessions they are registered in.

- **Session Assignment:**
	- A trainee cannot be assigned to overlapping sessions (same day, overlapping time).
	- A trainee cannot be assigned to the same session more than once.
	- Only trainers can create or manage sessions.

- **Absence Management:**
	- Absence can only be reported for future dates matching the session's scheduled day.
	- Duplicate absences (same trainee, session, and date) are not allowed.
	- Trainers can only report absences for trainees in their sessions.
	- Trainees can only report their own absences.

- **Data Integrity:**
	- All foreign keys (e.g., user/session IDs) are validated.
	- Attempts to operate on non-existent or unauthorized resources will raise clear errors.

---

# FastAPI & Docker

This repository provides a robust, production-ready backend for tennis club management, built with FastAPI and designed for containerized deployment. The stack leverages Docker for environment consistency and [uv](https://github.com/astral-sh/uv) for efficient Python dependency management. All core features are modular and extensible, making it easy to adapt for other club or scheduling use cases.

---

## 🚀 Features

- FastAPI application with modular structure
- Dockerized for easy development and deployment
- Modern Python dependency management with `uv` and `pyproject.toml`
- Pre-commit hooks for linting and formatting
- Example Makefile for common dev tasks
- Health check endpoint for service monitoring

---

## 🛠️ Prerequisites

- [uv](https://github.com/astral-sh/uv) (recommended for Python deps)
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

Install `uv`:

```sh
curl -Ls https://astral.sh/uv/install.sh | sh
```
Or see the [uv installation guide](https://github.com/astral-sh/uv#installation) for other methods.

---

## ⚡ Quick Start

1. **Build the development Docker image:**
	 ```sh
	 make build-dev
	 ```
2. **Start the development container:**
	 ```sh
	 make dev-up
	 ```
	 The app will be available at [http://localhost:8080](http://localhost:8080).

---

## 🧰 Development

- **Enable pre-commit hooks:**
	```sh
	pre-commit install
	```
	This will enable automatic linting and formatting on commit.

- **Run tests:**
	```sh
	make test-all
	```

---

## 📁 Project Structure

- `src/app/main.py` – FastAPI app entry point
- `src/app/routers/` – API route definitions
- `src/app/core/` – Core business logic and services
- `src/app/schemas/` – Pydantic/SQLModel schemas
- `provision/Dockerfile.dev` – Development Dockerfile
- `provision/entrypoint.sh` – Entrypoint script
- `pyproject.toml` – Python dependencies and tool config
- `Makefile` – Common dev commands

---

## 🩺 Health Check

Visit `/` to check if the app is running:

```
GET /
Response: "ok"
```

---

## 📚 More

- See `docs/` for additional setup and usage notes.
- Customize and extend as needed for your club's requirements!
