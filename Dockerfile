FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (layer cache)
COPY pyproject.toml uv.lock* ./

# Install dependencies (no dev group)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Create static dirs that must exist at runtime
RUN mkdir -p static/profile_pics

# Run with uv
CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
