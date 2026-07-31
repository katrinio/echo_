# Architecture

## Overview

echo_ is a personal milestone log — a small web app built with FastAPI, server-rendered via Jinja2, using SQLite as the data store.

## Stack

| Layer           | Technology                         |
|-----------------|------------------------------------|
| Web framework   | FastAPI                            |
| Templates       | Jinja2                             |
| ORM             | SQLAlchemy 2.x (Mapped API)        |
| Database        | SQLite (`user_data/echo.db` locally by default; configurable via `DATABASE_URL`) |
| Migrations      | Alembic                            |
| Form validation | Pydantic v2                        |
| Configuration   | Pydantic Settings                  |

## Structure

```
src/
  app.py            — FastAPI app, middleware, routers, lifespan
  config.py         — Settings (Pydantic), singleton settings instance
  database.py       — SQLAlchemy engine, Base
  main.py           — entry point
  runner.py         — echo-run command
  sitecustomize.py  — import path setup

  orm/
    milestone.py      — Milestone ORM model + query methods
    tag.py            — Tag ORM model + queries
    milestone_tags.py — many-to-many join table
    alembic.ini       — Alembic config
    migrations/       — env.py, script.py.mako, versions/

  web/
    templates.py      — shared Jinja2Templates, static_url, asset_version, settings in context

  features/
    auth/
      api.py          — GET/POST /login, GET /logout
      middleware.py   — AuthMiddleware (protects all routes except public ones)
      security.py     — sessions, password check, cookie

    milestones/
      api.py          — /, /new, /milestones/{slug}, /milestones/{slug}/edit
      dto.py          — MilestoneCreateDTO, MilestoneUpdateDTO
      helpers.py      — slug_from_title, normalize_tag
      services.py     — group_by_day, group_by_year_and_month

    tags/
      api.py          — /tags, /tags/{tag_name}

    terminal/
      api.py          — /help, /random, /search, /terminal/commands, /tree
      commands.py     — command list (COMMANDS)

  templates/
    base.html
    auth/
      login.html
    milestones/
      index.html, detail.html, new.html, edit.html
    tags/
      tags.html, tag.html
    terminal/
      help.html, search.html

  static/
    site.webmanifest
    css/
      base.css, forms.css
      pages/       timeline.css, milestone.css
      components/  terminal.css, terminal-table.css
    js/
      autocomplete/  core.js, tags.js, terminal.js
      keyboard/      global.js
      terminal/      input.js, input-mobile.js, navigation.js, table.js
    icons/
      favicon.ico, favicon-16x16.png, favicon-32x32.png
      apple-touch-icon-180x180.png
      pwa-icon-192x192.png, pwa-icon-256x256.png, pwa-icon-384x384.png, pwa-icon-512x512.png
      larger source/reserve icons
```

## Routes

| Method | Path                      | Action                             |
|--------|---------------------------|------------------------------------|
| GET    | `/`                       | Milestone list, grouped by day     |
| GET    | `/new`                    | Create milestone form              |
| POST   | `/new`                    | Create milestone                   |
| GET    | `/milestones/{slug}`      | Milestone detail page              |
| GET    | `/milestones/{slug}/edit` | Edit form                          |
| POST   | `/milestones/{slug}/edit` | Update milestone                   |
| GET    | `/tags`                   | All tags with counts               |
| GET    | `/tags/{tag}`             | Tag page                           |
| GET    | `/help`                   | Terminal commands                  |
| GET    | `/random`                 | Random milestone (redirect)        |
| GET    | `/search?q=`              | Search by title and description    |
| GET    | `/tree`                   | Chronological terminal journal     |
| GET    | `/login`                  | Login form                         |
| POST   | `/login`                  | Authenticate                       |
| GET    | `/logout`                 | Log out                            |
| GET    | `/terminal/commands`      | JSON command list for autocomplete |

## Authentication

All routes are protected by `AuthMiddleware`. Public exceptions: `/login`, `/logout`, `/health`, `/robots.txt`, `/static/*`.

The session is stored in an httponly cookie (`echo_session`), signed with `itsdangerous`. Sessions last 30 days. The cookie is `secure=True` only in `production`.

## Configuration

Read from `.env` via `pydantic-settings`. Variables:

| Variable             | Default                        | Description                            |
|----------------------|--------------------------------|----------------------------------------|
| `DATABASE_URL`       | `sqlite:///.../user_data/echo.db` | Database URL                        |
| `SESSION_SECRET_KEY` | —                              | Session signing key (required)         |
| `ECHO_PASSWORD`      | —                              | Login password (required)              |
| `ECHO_USERNAME`      | `katrin`                       | Username                               |
| `ENVIRONMENT`        | from system env, not from .env | `production` enables the secure cookie |

## Data models

### Milestone

```python
class Milestone(Base):
    id:           int       # primary key
    title:        str       # up to 255 characters
    slug:         str       # unique identifier (UPPER_SNAKE_CASE)
    description:  str       # defaults to ""
    happened_at:  date      # date of the event
    created_at:   datetime  # record creation time (UTC, auto-set)
    tags:         list[Tag] # many-to-many via milestone_tags
```

### Tag

```python
class Tag(Base):
    id:         int             # primary key
    name:       str             # unique name (UPPERCASE)
    milestones: list[Milestone] # back-reference
```

Join table `milestone_tags`: `milestone_id` + `tag_id` (composite PK).

## ORM

`src/orm/` contains plain models with query methods. `Base` and `milestone_tags` live in `database.py` to avoid circular imports.

Slugs are generated from the title automatically. Duplicates get a numeric suffix (`_2`, `_3`, ...). When editing, the slug is only recalculated if the title changed.

## Form validation

DTOs in `features/milestones/dto.py`:

- `title` — non-empty, `A-Za-z0-9 .-` only
- `happened_at` — cannot be in the future for the user's timezone
- `description` — whitespace stripped
- `tags` — split on spaces/commas, normalized to UPPERCASE

On validation error, the template is returned with an `error` field — no redirect.

## Terminal

The bottom bar is a navigation layer, not a shell. Commands: `help`, `new`, `tags`, `tag {name}`, `random`, `search {query}`, `tree`, `logout`. The command list is served at `/terminal/commands` and used for autocomplete.

## Cache policy

- HTML responses should not be cached long-term.
- Versioned static assets should be cached long-term (`Cache-Control: public, max-age=31536000, immutable`).
- All template static references should use `static_url(request, ...)` so URLs include cache versions and respect ASGI `root_path`.

## Timeline

`/tree` renders a chronological terminal journal using data grouped by year, month, and day. The backend helper `group_by_year_and_month` returns nested `OrderedDict` values in the shape `Year -> Month -> Day -> [Milestone]` so the template can render plain text-style output with stable alignment.

## Migrations

| Revision       | Description                      |
|----------------|----------------------------------|
| `733b95b80ad6` | Create milestones table          |
| `4f1b2d9c7a11` | Add tags and milestone_tags      |

```bash
poetry run alembic -c src/orm/alembic.ini upgrade head
```

## Running

```bash
poetry run echo-run
```

Tables are created automatically on first run via `lifespan`. Afterwards, stamp the current revision:

```bash
poetry run alembic -c src/orm/alembic.ini stamp 4f1b2d9c7a11
```

## Code quality

Pre-commit hooks: Ruff, MyPy, djLint, Stylelint, ESLint, pytest, JS tests (Vitest), poetry check, alembic check.  
In pre-commit, linters run on changed files where possible; MyPy, pytest, JS tests, poetry check and alembic check run as full-project checks. CI runs full checks.

CI (`.github/workflows/`):
- `quality_gates.yml` — Python style, Frontend style, Python tests, JS tests, Migrations
- `smoke.yml` — runs after quality gates and executes middleware smoke tests
- `release.yml` — semantic-release, publishes a draft release on push to main
