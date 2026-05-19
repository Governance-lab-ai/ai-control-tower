from logging.config import fileConfig

from alembic import context

from app.core.config import get_settings
from app.models import AISystem, AuditEvent, ModelRun, PromptVersion, RetrievedDocument
from app.models.base import Base

_ = (AISystem, AuditEvent, ModelRun, PromptVersion, RetrievedDocument)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online() -> None:
    settings = get_settings()
    config.set_main_option("sqlalchemy.url", settings.database_url)
    connectable = context.config.attributes.get("connection")

    if connectable is not None:
        context.configure(connection=connectable, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
        return

    if connectable is None:
        from sqlalchemy import create_engine

        connectable = create_engine(settings.database_url, pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
