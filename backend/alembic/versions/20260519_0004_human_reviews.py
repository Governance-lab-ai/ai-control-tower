"""human reviews

Revision ID: 20260519_0004
Revises: 20260519_0003
Create Date: 2026-05-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "20260519_0004"
down_revision: str | None = "20260519_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "human_reviews" in inspector.get_table_names():
        return

    op.create_table(
        "human_reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ai_system_id", sa.Uuid(), nullable=False),
        sa.Column("model_run_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.String(length=120), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("reviewer_id", sa.String(length=120), nullable=True),
        sa.Column("reviewer_name", sa.String(length=160), nullable=True),
        sa.Column("decision_notes", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ai_system_id"], ["ai_systems.id"]),
        sa.ForeignKeyConstraint(["model_run_id"], ["model_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_human_reviews_ai_system_id"), "human_reviews", ["ai_system_id"], unique=False)
    op.create_index(op.f("ix_human_reviews_model_run_id"), "human_reviews", ["model_run_id"], unique=False)
    op.create_index(op.f("ix_human_reviews_priority"), "human_reviews", ["priority"], unique=False)
    op.create_index(op.f("ix_human_reviews_reason"), "human_reviews", ["reason"], unique=False)
    op.create_index(op.f("ix_human_reviews_status"), "human_reviews", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_human_reviews_status"), table_name="human_reviews")
    op.drop_index(op.f("ix_human_reviews_reason"), table_name="human_reviews")
    op.drop_index(op.f("ix_human_reviews_priority"), table_name="human_reviews")
    op.drop_index(op.f("ix_human_reviews_model_run_id"), table_name="human_reviews")
    op.drop_index(op.f("ix_human_reviews_ai_system_id"), table_name="human_reviews")
    op.drop_table("human_reviews")
