import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_system_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_systems.id"), nullable=False, index=True)
    model_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("model_runs.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    reason: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium", index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewer_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    decision_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    model_run: Mapped["ModelRun"] = relationship("ModelRun", back_populates="human_reviews")
