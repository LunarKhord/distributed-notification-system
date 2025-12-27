# 1. Base image: Python-slim
FROM python:3.11-slim

# 2. Environment Variables:
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Critical: Tell uv to create the virtual environment in a predictable spot
ENV UV_PROJECT_ENVIRONMENT="/app/.venv"

# 3. Equip the System: Install 'uv' globally
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 4. Define the Workspace
WORKDIR /app

# 5. Install System Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 6. Dependency Synchronization
COPY pyproject.toml uv.lock ./

# Use --no-install-project to cache the heavy dependency layer
RUN uv sync --frozen --no-install-project --no-dev

# 7. Copy Application Code
COPY . .

# 8. Final Project Sync 
# This layer installs your 'main.py' and project logic
RUN uv sync --frozen --no-dev

# 9. Execution
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--reload", "--port", "8000"]