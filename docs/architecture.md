# Архитектура проекта

## Обзор

echo_ — личный лог вех. Небольшое веб-приложение на FastAPI с SSR через Jinja2 и SQLite в качестве хранилища.

## Стек

| Слой         | Технология                        |
|--------------|-----------------------------------|
| Веб-фреймворк | FastAPI                          |
| Шаблоны      | Jinja2                            |
| ORM          | SQLAlchemy 2.x (Mapped API)       |
| БД           | SQLite (`echo.db` в корне проекта) |
| Миграции     | Alembic                           |
| Валидация форм | Pydantic v2                     |
| Интерактивность | HTMX (планируется)             |

## Структура

```
src/
  core/
    app.py          — FastAPI app, монтирование статики, on_startup
    database.py     — SQLAlchemy engine

  milestones/
    models.py       — ORM-модель Milestone + методы запросов
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

| Метод | Путь                     | Действие                    |
|-------|--------------------------|-----------------------------|
| GET   | `/`                      | Список вех, сгруппированных по дню |
| GET   | `/new`                   | Форма создания вехи         |
| POST  | `/new`                   | Создать веху                |
| GET   | `/milestones/{slug}`     | Детальная страница вехи     |
| GET   | `/milestones/{slug}/edit`| Форма редактирования        |
| POST  | `/milestones/{slug}/edit`| Обновить веху               |

## Модель данных

```python
class Milestone(Base):
    id:           int       # первичный ключ
    title:        str       # название (до 255 символов)
    slug:         str       # уникальный идентификатор (UPPER_SNAKE_CASE)
    description:  str       # описание, по умолчанию ""
    happened_at:  date      # дата события
    created_at:   datetime  # дата записи (UTC, проставляется автоматически)
```

Slug генерируется из title автоматически. При дубликате добавляется суффикс (`_2`, `_3`, ...).

## Валидация форм

Валидация вынесена в Pydantic-DTO до модельного слоя:

- `title` — не пустой после trim, только английские буквы, цифры, пробелы, `.` и `-`
- `happened_at` — не в будущем
- `description` — strip пробелов

При ошибке роут возвращает шаблон формы с сообщением `error`, без редиректа.

## CSS

Каждый файл отвечает за свой контекст. `forms.css` и страничные CSS подключаются через `{% block styles %}` в конкретных шаблонах, не глобально.

## Запуск

```bash
PYTHONPATH=src poetry run uvicorn main:app --reload
```

Первый запуск создаёт таблицы автоматически через `on_startup`. Для миграций:

```bash
PYTHONPATH=src .venv/bin/alembic upgrade head
```

## Качество кода

Pre-commit хуки: Ruff, MyPy, djLint, pytest, Stylelint.

CI (GitHub Actions): те же проверки на push и pull request в `main`.
