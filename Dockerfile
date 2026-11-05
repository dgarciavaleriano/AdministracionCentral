FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /bin/uv

WORKDIR /app

# Primero solo las dependencias: así Docker las cachea mientras no cambie uv.lock.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./
COPY migrations ./migrations
COPY src ./src

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

# Al arrancar aplica las migraciones pendientes y levanta la API.
CMD ["sh", "-c", "alembic upgrade head && python src/main.py"]
