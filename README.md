## FastAPI Docker Template

This project provides a template for running a FastAPI application inside a Docker container, with modern Python dependency management using uv and pyproject.toml.

## Prerequisites

This project requires [uv](https://github.com/astral-sh/uv) for Python dependency management. Install it with:

```sh
curl -Ls https://astral.sh/uv/install.sh | sh
```

Or see the [uv installation guide](https://github.com/astral-sh/uv#installation) for other methods.

### Features
- FastAPI app with a simple health check endpoint
- Dockerfile for development and production
- uv for fast dependency management
- Example Makefile for build and up commands
- Pre-commit hooks for linting/formatting

### Quick Start
1. Build the Docker image:
	```sh
	make build-dev
	```
2. Start the development container:
	```sh
	make dev-up
	```

The app will be available at http://localhost:8080.

#### Enable Pre-commit Hooks
After cloning the repo, run:
```sh
pre-commit install
```
This will enable automatic linting and formatting on commit.

### Project Structure
- `src/app/main.py`: FastAPI app entry point
- `provision/Dockerfile.dev`: Development Dockerfile
- `provision/entrypoint.sh`: Entrypoint script
- `pyproject.toml`: Python dependencies

### Health Check
Visit `/` to check if the app is running:
```
GET /
Response: "ok"
```
