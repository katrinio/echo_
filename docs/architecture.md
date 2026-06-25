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
  app.py            — FastAPI app, монтирование статики, подключение роутеров, on_startup
  database.py       — SQLAlchemy engine

  orm/
    milestone.py     — ORM-модель Milestone + методы запросов
    tag.py           — ORM-модель Tag + запросы по тегам
    milestone_tags.py — таблица связи many-to-many

  web/
    templates.py     — общий helper для Jinja2Templates

  features/
    milestones/
      api.py        — APIRouter для /, /new, /milestones/*
      dto.py        — MilestoneCreateDTO, MilestoneUpdateDTO (Pydantic)
      helpers.py    — нормализация и валидация тегов
      services.py   — вспомогательные операции с milestones
      commands.py   — команды терминального help
    tags/
      api.py        — маршруты /tags и /tags/{tag}
      services.py   — вспомогательные запросы по тегам
    terminal/
      api.py        — /help и /random
      commands.py   — список терминальных команд

  templates/
    base.html       — базовый шаблон (шапка, терминальная строка)
    milestones/
      index.html    — главная страница, список вех по дням
      detail.html   — страница отдельной вехи
      new.html      — форма создания
      edit.html     — форма редактирования
    tags/
      tags.html     — список тегов
      tag.html      — страница отдельного тега
    terminal/
      help.html     — список доступных терминальных команд

  static/css/
    base.css        — переменные, body, layout, ссылки
    forms.css       — формы создания и редактирования
    pages/
      timeline.css  — дерево вех на главной
      milestone.css — страница детали вехи
    components/
      terminal.css  — терминальная строка внизу страницы
      terminal-table.css — терминальные таблицы

  static/js/
    tag-autocomplete.js     — автодополнение тегов
    terminal-input.js       — диспетчер терминальных команд
    terminal-input-mobile.js — мобильное поведение терминального input
    terminal-table.js       — универсальный форматтер терминальных таблиц

  main.py           — точка входа, реэкспортирует app
  runner.py         — команды запуска `echo-run` и `echo-dev`
  sitecustomize.py   — настройка import path

tests/
  test_*.py        — тесты валидации, моделей и маршрутов

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
| GET   | `/tags`                   | Список всех тегов с количеством    |
| GET   | `/tags/{tag}`             | Страница тега                      |
| GET   | `/help`                   | Справка по терминальным командам    |
| GET   | `/random`                 | Случайная веха                     |

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
- `tags` — строка разбивается по пробелам и запятым, каждый тег приводится к `UPPERCASE`, допускаются только `A-Z`, `0-9`, `_`, длина 1..32

`Tag` и `slug` — разные сущности:

- `slug` — URL-friendly идентификатор для страниц вех;
- `tag` — терминальный label для фильтрации и отображения списков.

При ошибке роут возвращает шаблон формы с сообщением `error`, без редиректа.

## Миграции

Alembic управляет схемой БД. Текущие миграции:

| Ревизия        | Описание                    |
|----------------|-----------------------------|
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

`terminal-table.js` используется для терминальных таблиц по `data-terminal-table` / `data-terminal-table-row` и пересчитывает точки по ширине реального gap между label и value.

`terminal-input.js` содержит диспетчер команд, а `terminal-input-mobile.js` — только мобильное поведение при фокусе в терминальном input.

## Запуск

```bash
poetry run echo-run
```

Первый запуск создаёт таблицы автоматически через `on_startup`. После этого нужно проставить ревизию Alembic:

```bash
poetry run alembic upgrade head
poetry run alembic stamp 4f1b2d9c7a11
```

## Качество кода

Pre-commit хуки: Ruff, MyPy, djLint, Stylelint, pytest, poetry lock check.

Линтеры (кроме MyPy и pytest) запускаются только на изменённые файлы.

CI (GitHub Actions): те же проверки + отдельный job для миграций (`alembic upgrade head` + `alembic check`).
