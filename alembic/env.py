import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

CONFIG = context.config

if CONFIG.config_file_name is not None:
    fileConfig(CONFIG.config_file_name)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import Base  # noqa: E402

import src.orm.milestone  # noqa: F401, E402
import src.orm.tag  # noqa: F401, E402

target_metadata = Base.metadata
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    CONFIG.get_main_option("sqlalchemy.url"),
)

CONFIG.set_main_option("sqlalchemy.url", DATABASE_URL)

print(f"DATABASE_URL={DATABASE_URL}")


def run_migrations_offline() -> None:
    url = CONFIG.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        CONFIG.get_section(CONFIG.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
