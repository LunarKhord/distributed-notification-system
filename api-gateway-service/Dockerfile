# 1. Base image: Python-slim
FROM python:3.11-slim

# 2. Environment Variables:
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Ensure the virtual environment uv creates is automatically used
ENV PATH="/app/.venv/bin:$PATH"

# 3. Equip the System: Install 'uv' globally before entering the workspace
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 4. Define the Workspace
WORKDIR /app

# 5. Install System Dependencies (Postgres & Build Tools)
# Combined into one RUN to reduce layer bloat
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 6. Dependency Synchronization (The "Heavy" cached layer)
# You need both files for 'uv sync' to verify the environment
COPY pyproject.toml uv.lock ./

# --frozen: Prevents uv from updating the lockfile (ensures reproducibility)
# --no-install-project: Installs dependencies WITHOUT your app code yet (better caching)
RUN uv sync --frozen --no-install-project --no-dev

# 7. Copy Application Code (The "Frequently Changing" layer)
COPY . .

# 8. Final Project Sync (Installs your actual package/app)
RUN uv sync --frozen --no-dev

# 9. Execution: Note the addition of commas in the JSON array
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]