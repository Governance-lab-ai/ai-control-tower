"""run steps

Revision ID: 20260520_0005
Revises: 20260519_0004
Create Date: 2026-05-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "20260520_0005"
down_revision: str | None = "20260519_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "run_steps" in inspector.get_table_names():
        return

    op.create_table(
        "run_steps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("model_run_id", sa.Uuid(), nullable=False),
        sa.Column("step_type", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column("output_summary", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["model_run_id"], ["model_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_run_steps_model_run_id"), "run_steps", ["model_run_id"], unique=False)
    op.create_index(op.f("ix_run_steps_status"), "run_steps", ["status"], unique=False)
    op.create_index(op.f("ix_run_steps_step_type"), "run_steps", ["step_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_run_steps_step_type"), table_name="run_steps")
    op.drop_index(op.f("ix_run_steps_status"), table_name="run_steps")
    op.drop_index(op.f("ix_run_steps_model_run_id"), table_name="run_steps")
    op.drop_table("run_steps")
