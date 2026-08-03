FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.2.1

COPY pyproject.toml poetry.lock README.md ./

FROM base AS production

ARG ECHO_VERSION

ENV ECHO_HOST=0.0.0.0 \
    ECHO_PORT=8000 \
    ECHO_ENV=production \
    ECHO_VERSION=${ECHO_VERSION} \
    DATABASE_URL=sqlite:////app/echo.db

COPY src ./src
COPY scripts ./scripts

RUN python -c "from src.version import get_version_string; get_version_string()"

RUN poetry install --only main --no-root

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
