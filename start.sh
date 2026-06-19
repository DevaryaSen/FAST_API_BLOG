#!/usr/bin/env bash
# Start the blog dev server. Keep this terminal open while browsing.
cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. See README.md for setup."
  exit 1
fi

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit SECRET_KEY if needed."
fi

echo "Starting server at http://127.0.0.1:8000"
echo "Press Ctrl+C to stop."
exec uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
