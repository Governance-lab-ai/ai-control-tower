"""evaluations

Revision ID: 20260519_0003
Revises: 20260519_0002
Create Date: 2026-05-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "20260519_0003"
down_revision: str | None = "20260519_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "evaluations" in inspector.get_table_names():
        return

    op.create_table(
        "evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("model_run_id", sa.Uuid(), nullable=False),
        sa.Column("ai_system_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("evaluation_score", sa.Integer(), nullable=False),
        sa.Column("relevance_score", sa.Integer(), nullable=False),
        sa.Column("groundedness_score", sa.Integer(), nullable=False),
        sa.Column("hallucination_flag", sa.Boolean(), nullable=False),
        sa.Column("evaluation_summary", sa.Text(), nullable=False),
        sa.Column("requires_human_review", sa.Boolean(), nullable=False),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ai_system_id"], ["ai_systems.id"]),
        sa.ForeignKeyConstraint(["model_run_id"], ["model_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_run_id"),
    )
    op.create_index(op.f("ix_evaluations_ai_system_id"), "evaluations", ["ai_system_id"], unique=False)
    op.create_index(op.f("ix_evaluations_model_run_id"), "evaluations", ["model_run_id"], unique=True)
    op.create_index(op.f("ix_evaluations_requires_human_review"), "evaluations", ["requires_human_review"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_evaluations_requires_human_review"), table_name="evaluations")
    op.drop_index(op.f("ix_evaluations_model_run_id"), table_name="evaluations")
    op.drop_index(op.f("ix_evaluations_ai_system_id"), table_name="evaluations")
    op.drop_table("evaluations")
