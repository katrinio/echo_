# Архитектура проекта

## Обзор

echo_ — личный лог вех. Небольшое веб-приложение на FastAPI с SSR через Jinja2 и SQLite в качестве хранилища.

## Стек

| Слой           | Технология                         |
|----------------|------------------------------------|
| Веб-фреймворк  | FastAPI                            |
| Шаблоны        | Jinja2                             |
| ORM            | SQLAlchemy 2.x (Mapped API)        |
| БД             | SQLite (`echo.db` в корне проекта) |
| Миграции       | Alembic                            |
| Валидация форм | Pydantic v2                        |
| Конфигурация   | Pydantic Settings                  |

## Структура

```
src/
  app.py            — FastAPI app, middleware, роутеры, on_startup
  config.py         — Settings (Pydantic), единственный экземпляр settings
  database.py       — SQLAlchemy engine, Base
  main.py           — точка входа
  runner.py         — команда echo-run
  sitecustomize.py  — настройка import path

  orm/
    milestone.py      — ORM-модель Milestone + методы запросов
    tag.py            — ORM-модель Tag + запросы
    milestone_tags.py — таблица связи many-to-many
    alembic.ini       — конфиг Alembic
    migrations/       — env.py, script.py.mako, versions/

  web/
    templates.py      — общий Jinja2Templates, asset_version, settings в контексте

  features/
    auth/
      api.py          — GET/POST /login, GET /logout
      middleware.py   — AuthMiddleware (защита всех маршрутов кроме публичных)
      security.py     — сессии, проверка пароля, cookie

    milestones/
      api.py          — /, /new, /milestones/{slug}, /milestones/{slug}/edit
      dto.py          — MilestoneCreateDTO, MilestoneUpdateDTO
      helpers.py      — slug_from_title, normalize_tag
      services.py     — group_by_day

    tags/
      api.py          — /tags, /tags/{tag_name}
      services.py     — get_milestones_for_tag

    terminal/
      api.py          — /help, /random, /search, /terminal/commands
      commands.py     — список команд (COMMANDS)

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
    css/
      base.css, forms.css
      pages/    timeline.css, milestone.css
      components/  terminal.css, terminal-table.css
    js/
      autocomplete/  core.js, tags.js, terminal.js
      keyboard/      global.js
      terminal/      input.js, input-mobile.js, navigation.js, table.js
    icons/
      favicon.ico, favicon.svg, apple-touch-icon.png
```

## Маршруты

| Метод | Путь                      | Действие                           |
|-------|---------------------------|------------------------------------|
| GET   | `/`                       | Список вех, сгруппированных по дню |
| GET   | `/new`                    | Форма создания вехи                |
| POST  | `/new`                    | Создать веху                       |
| GET   | `/milestones/{slug}`      | Детальная страница вехи            |
| GET   | `/milestones/{slug}/edit` | Форма редактирования               |
| POST  | `/milestones/{slug}/edit` | Обновить веху                      |
| GET   | `/tags`                   | Список всех тегов с количеством    |
| GET   | `/tags/{tag}`             | Страница тега                      |
| GET   | `/help`                   | Терминальные команды               |
| GET   | `/random`                 | Случайная веха (редирект)          |
| GET   | `/search?q=`              | Поиск по названию и описанию       |
| GET   | `/login`                  | Форма входа                        |
| POST  | `/login`                  | Аутентификация                     |
| GET   | `/logout`                 | Выход                              |
| GET   | `/terminal/commands`      | JSON-список команд для автодополнения |

## Аутентификация

Все маршруты защищены `AuthMiddleware`. Исключения: `/login`, `/logout`, `/health`, `/static/*`.

Сессия хранится в httponly cookie (`echo_session`), подписанной через `itsdangerous`. Срок — 30 дней. Cookie `secure=True` только в `production`.

## Конфигурация

Читается из `.env` через `pydantic-settings`. Переменные:

| Переменная          | По умолчанию                  | Описание                     |
|---------------------|-------------------------------|------------------------------|
| `DATABASE_URL`      | `sqlite:///echo.db`           | URL базы данных              |
| `SESSION_SECRET_KEY`| —                             | Ключ подписи сессии (обязательно) |
| `ECHO_PASSWORD`     | —                             | Пароль входа (обязательно)   |
| `ECHO_USERNAME`     | `katrin`                      | Имя пользователя             |
| `ENVIRONMENT`       | из системного env, не из .env | `production` влияет на secure cookie |

## Модели данных

### Milestone

```python
class Milestone(Base):
    id:           int       # первичный ключ
    title:        str       # название (до 255 символов)
    slug:         str       # уникальный идентификатор (UPPER_SNAKE_CASE)
    description:  str       # описание, по умолчанию ""
    happened_at:  date      # дата события
    created_at:   datetime  # дата записи (UTC, автоматически)
    tags:         list[Tag] # many-to-many через milestone_tags
```

### Tag

```python
class Tag(Base):
    id:         int             # первичный ключ
    name:       str             # уникальное название (UPPERCASE)
    milestones: list[Milestone] # обратная связь
```

Таблица связи `milestone_tags`: `milestone_id` + `tag_id` (составной PK).

## ORM

`src/orm/` — чистые модели с методами запросов. `Base` и `milestone_tags` живут в `database.py` чтобы избежать circular imports.

Slug генерируется из title автоматически. При дубликате добавляется суффикс (`_2`, `_3`, ...). При редактировании slug пересчитывается только если изменился title.

## Валидация форм

DTO в `features/milestones/dto.py`:

- `title` — не пустой, только `A-Za-z0-9 .-`
- `happened_at` — не в будущем
- `description` — strip пробелов
- `tags` — разбивается по пробелам/запятым, приводится к UPPERCASE

При ошибке — возврат шаблона с `error`, без редиректа.

## Терминал

Нижняя строка — навигационный слой, не shell. Команды: `help`, `new`, `tags`, `tag {name}`, `random`, `search {query}`, `logout`. Список команд отдаётся через `/terminal/commands` и используется для автодополнения.

## Миграции

| Ревизия        | Описание                            |
|----------------|-------------------------------------|
| `733b95b80ad6` | Создание таблицы milestones         |
| `4f1b2d9c7a11` | Добавление tags и milestone_tags    |

```bash
poetry run alembic -c src/orm/alembic.ini upgrade head
```

## Запуск

```bash
poetry run echo-run
```

Таблицы создаются автоматически при первом запуске через `lifespan`. После — проставить ревизию:

```bash
poetry run alembic -c src/orm/alembic.ini stamp 4f1b2d9c7a11
```

## Качество кода

Pre-commit хуки: Ruff, MyPy, djLint, Stylelint, ESLint, pytest, JS-тесты (Vitest), poetry check, alembic check.  
Линтеры (кроме MyPy и pytest) — только на изменённые файлы.

CI (`.github/workflows/`):
- `quality_gates.yml` — Python style, Frontend style, Python tests, JS tests, Migrations
- `smoke.yml` — запускается после quality gates, поднимает сервер и проверяет `/login`
- `release.yml` — semantic-release, публикует черновик релиза при пуше в main
