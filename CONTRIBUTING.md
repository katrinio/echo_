# Contributing

echo_ is a small personal project, but PRs and issues are welcome.

## Before you start

- Architecture and routes — [docs/architecture.md](docs/architecture.md)
- Keyboard controls — [docs/controls.md](docs/controls.md)
- Development setup — [docs/development.md](docs/development.md)
- Commit and release conventions — [docs/releases.md](docs/releases.md)

## Setup

```bash
poetry install
npm install
pre-commit install
```

Copy `.env.example` to `.env` and fill in the required values.

## Before a PR

```bash
# Python
poetry run ruff check src
poetry run mypy src
poetry run pytest

# JS
npx eslint "src/static/js/**/*.js"
./node_modules/.bin/stylelint "src/static/css/**/*.css"
npm run test:js
```

All of these run in CI on every PR — a failing check won't get merged.

## Style

- New features go in `src/features/`, following the existing structure (`api.py`, `services.py`, `dto.py`).
- Templates live in `src/templates/`, JavaScript in `src/static/js/`.
- The terminal bar is a navigation layer, not a shell — keep commands simple and purposeful.
- Form validation belongs in DTOs (`dto.py`), not in route handlers.
- Tests are expected for new Python logic; JS tests for anything in `src/static/js/`.

## Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/). See [docs/releases.md](docs/releases.md) for the full type list and examples. Only `feat` and `fix` bump the version.

## PR

- Keep it small and focused on one thing.
- If it changes a route, the terminal commands, or the data model — update [docs/architecture.md](docs/architecture.md) in the same PR.
