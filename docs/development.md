## Development

### Install

```bash
poetry install
npm install
```

Copy `.env.example` to `.env` and fill in the required values.

### Run

```bash
poetry run echo-run
```

Open the app at `http://127.0.0.1:8000`.

### Database

Apply migrations:

```bash
poetry run alembic -c src/orm/alembic.ini upgrade head
```

Seed local data:

```bash
poetry run python scripts/seed_echo.py
```

If the database already has tables and you need to align Alembic with the current schema:

```bash
poetry run alembic -c src/orm/alembic.ini stamp 4f1b2d9c7a11
```

### Tests

```bash
# Python
poetry run pytest
poetry run pytest --cov=src --cov-report=html  # with coverage

# JS
npm run test:js
npm run test:js:coverage  # with coverage, opens htmlcov equivalent in coverage/
```

### Checks

```bash
# Python
poetry run ruff check src
poetry run mypy src
poetry run djlint src/templates --check

# JS
./node_modules/.bin/stylelint "src/static/css/**/*.css"
npx eslint "src/static/js/**/*.js"
```
