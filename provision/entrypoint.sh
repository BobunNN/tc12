#!/bin/sh
uv run python -m src.scripts.init_db
uv run uvicorn src.app.main:app --reload --port 8081 --host 0.0.0.0
