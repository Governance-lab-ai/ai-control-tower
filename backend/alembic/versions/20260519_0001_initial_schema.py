"""initial local schema

Revision ID: 20260519_0001
Revises:
Create Date: 2026-05-19
"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import inspect

from app.models import AISystem, AuditEvent, Incident, ModelRun, PromptVersion, RetrievedDocument
from app.models.base import Base

revision: str = "20260519_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ = (AISystem, AuditEvent, Incident, ModelRun, PromptVersion, RetrievedDocument)


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

    inspector = inspect(bind)
    if "model_runs" in inspector.get_table_names():
        output_text = next((column for column in inspector.get_columns("model_runs") if column["name"] == "output_text"), None)
        if output_text is not None and output_text.get("nullable") is False and bind.dialect.name != "sqlite":
            op.alter_column("model_runs", "output_text", existing_type=output_text["type"], nullable=True)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
