import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_system_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_systems.id"), nullable=False, index=True)
    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("prompt_versions.id"), nullable=True, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    input_pii_result: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    output_pii_result: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    retrieved_documents: Mapped[list["RetrievedDocument"]] = relationship(
        "RetrievedDocument",
        back_populates="model_run",
        cascade="all, delete-orphan",
        order_by="RetrievedDocument.ordinal",
    )
    evaluation: Mapped["Evaluation | None"] = relationship(
        "Evaluation",
        back_populates="model_run",
        cascade="all, delete-orphan",
        uselist=False,
    )
    human_reviews: Mapped[list["HumanReview"]] = relationship(
        "HumanReview",
        back_populates="model_run",
        cascade="all, delete-orphan",
        order_by="HumanReview.created_at.desc()",
    )


class RetrievedDocument(Base):
    __tablename__ = "retrieved_documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("model_runs.id"), nullable=False, index=True)
    source_label: Mapped[str] = mapped_column(String(160), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    model_run: Mapped[ModelRun] = relationship("ModelRun", back_populates="retrieved_documents")
