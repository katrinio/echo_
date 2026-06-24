FROM python:3.14-slim

WORKDIR /app

RUN pip install poetry==2.2.1

COPY pyproject.toml poetry.lock README.md ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --without dev --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
