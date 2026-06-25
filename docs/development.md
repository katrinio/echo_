## Development

### Install

```bash
poetry install
```

### Run

```bash
poetry run echo-run
```

Open the app at `http://127.0.0.1:8000`.

### Run in dev mode

```bash
poetry run echo-dev
```

This starts the app with `sqlite:///echo_dev.db`.

### Alternative local start

```bash
poetry run uvicorn src.app:app --reload
```

### Database

Apply migrations:

```bash
poetry run alembic upgrade head
```

If the database already has tables and you need to align Alembic with the current schema:

```bash
poetry run alembic stamp 4f1b2d9c7a11
```

### Checks

```bash
poetry run pytest
poetry run ruff check .
poetry run mypy src
poetry run djlint src/templates --check
poetry run stylelint "src/static/css/**/*.css"
```
