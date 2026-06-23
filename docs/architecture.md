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

## Структура

```
src/
  core/
    app.py          — FastAPI app, монтирование статики, on_startup
    database.py     — SQLAlchemy engine

  orm/
    base.py         — DeclarativeBase
    milestone.py    — ORM-модель Milestone + методы запросов
    tags.py         — ORM-модель Tag
    milestone_tags.py — таблица связи many-to-many

  models.py         — публичный реэкспорт всех ORM-моделей

  milestones/
    dto.py          — MilestoneCreateDTO, MilestoneUpdateDTO (Pydantic)
    routes.py       — APIRouter, все маршруты /milestones/*
    slug.py         — генерация и нормализация slug

  templates/
    base.html       — базовый шаблон (шапка, терминальная строка)
    milestones/
      index.html    — главная страница, список вех по дням
      detail.html   — страница отдельной вехи
      new.html      — форма создания
      edit.html     — форма редактирования

  static/css/
    base.css        — переменные, body, layout, ссылки
    timeline.css    — дерево вех на главной
    milestone.css   — страница детали вехи
    terminal.css    — терминальная строка внизу страницы
    forms.css       — формы создания и редактирования

  main.py           — точка входа, реэкспортирует app из core

tests/
  test_dto.py             — валидация DTO (11 тестов)
  test_slug_generation.py — генерация slug (2 теста)

docs/
  architecture.md   — этот файл
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

## Модели данных

### Milestone

```bash
class Milestone(Base):
    id:           int       # первичный ключ
    title:        str       # название (до 255 символов)
    slug:         str       # уникальный идентификатор (UPPER_SNAKE_CASE)
    description:  str       # описание, по умолчанию ""
    happened_at:  date      # дата события
    created_at:   datetime  # дата записи (UTC, проставляется автоматически)
    tags:         list[Tag] # теги (many-to-many через milestone_tags)
```

### Tag

```bash
class Tag(Base):
    id:         int             # первичный ключ
    name:       str             # название тега (уникальное, до 255 символов)
    milestones: list[Milestone] # обратная связь
```

### milestone_tags

Таблица связи many-to-many между `milestones` и `tags`:

| Колонка      | Тип     |
|--------------|---------|
| milestone_id | Integer |
| tag_id       | Integer |

## ORM

Модели разделены по файлам в `src/orm/`. Публичный интерфейс — `src/models.py`, который реэкспортирует `Base`, `Milestone`, `Tag`, `milestone_tags`.

Slug генерируется из title автоматически. При дубликате добавляется суффикс (`_2`, `_3`, ...).

## Валидация форм

Валидация вынесена в Pydantic-DTO до модельного слоя:

- `title` — не пустой после trim, только английские буквы, цифры, пробелы, `.` и `-`
- `happened_at` — не в будущем
- `description` — strip пробелов

При ошибке роут возвращает шаблон формы с сообщением `error`, без редиректа.

## Миграции

Alembic управляет схемой БД. Текущие миграции:

| Ревизия        | Описание                  |
|----------------|---------------------------|
| `733b95b80ad6` | Создание таблицы milestones |
| `4f1b2d9c7a11` | Добавление таблиц tags и milestone_tags |

Применить миграции:

```bash
poetry run alembic upgrade head
```

Если таблицы уже созданы через `create_all` (первый запуск), проставить текущую ревизию без выполнения SQL:

```bash
poetry run alembic stamp 4f1b2d9c7a11
```

## CSS

Каждый файл отвечает за свой контекст. `forms.css` и страничные CSS подключаются через `{% block styles %}` в конкретных шаблонах, не глобально.

## Запуск

```bash
PYTHONPATH=src poetry run uvicorn main:app --reload
```

Первый запуск создаёт таблицы автоматически через `on_startup`. После этого нужно проставить ревизию Alembic:

```bash
poetry run alembic stamp 4f1b2d9c7a11
```

## Качество кода

Pre-commit хуки: Ruff, MyPy, djLint, Stylelint, pytest, poetry lock check.

Линтеры (кроме MyPy и pytest) запускаются только на изменённые файлы.

CI (GitHub Actions): те же проверки + отдельный job для миграций (`alembic upgrade head` + `alembic check`).
