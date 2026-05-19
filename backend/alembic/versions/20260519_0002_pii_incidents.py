"""pii results and incidents

Revision ID: 20260519_0002
Revises: 20260519_0001
Create Date: 2026-05-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "20260519_0002"
down_revision: str | None = "20260519_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    model_run_columns = {column["name"] for column in inspector.get_columns("model_runs")}
    if "input_pii_result" not in model_run_columns:
        op.add_column("model_runs", sa.Column("input_pii_result", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    if "output_pii_result" not in model_run_columns:
        op.add_column("model_runs", sa.Column("output_pii_result", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))

    if "incidents" not in inspector.get_table_names():
        op.create_table(
            "incidents",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("ai_system_id", sa.Uuid(), nullable=False),
            sa.Column("model_run_id", sa.Uuid(), nullable=True),
            sa.Column("incident_type", sa.String(length=80), nullable=False),
            sa.Column("severity", sa.String(length=20), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["ai_system_id"], ["ai_systems.id"]),
            sa.ForeignKeyConstraint(["model_run_id"], ["model_runs.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_incidents_ai_system_id"), "incidents", ["ai_system_id"], unique=False)
        op.create_index(op.f("ix_incidents_incident_type"), "incidents", ["incident_type"], unique=False)
        op.create_index(op.f("ix_incidents_model_run_id"), "incidents", ["model_run_id"], unique=False)
        op.create_index(op.f("ix_incidents_severity"), "incidents", ["severity"], unique=False)
        op.create_index(op.f("ix_incidents_status"), "incidents", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_incidents_status"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_severity"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_model_run_id"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_incident_type"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_ai_system_id"), table_name="incidents")
    op.drop_table("incidents")
    op.drop_column("model_runs", "output_pii_result")
    op.drop_column("model_runs", "input_pii_result")
