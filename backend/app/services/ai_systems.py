from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_system import AISystem
from app.schemas.ai_system import AISystemCreate, ApprovalStatusUpdate
from app.services.audit import create_audit_event


LOCAL_ACTOR = "local_mock:governance_admin"


def create_ai_system(db: Session, payload: AISystemCreate) -> AISystem:
    system = AISystem(**payload.model_dump())
    db.add(system)
    db.flush()
    create_audit_event(
        db,
        actor=LOCAL_ACTOR,
        action="ai_system.created",
        entity_type="ai_system",
        entity_id=system.id,
        summary=f"AI system registered: {system.name}",
        metadata={
            "risk_level": system.risk_level,
            "approval_status": system.approval_status,
            "department": system.department,
        },
    )
    db.commit()
    db.refresh(system)
    return system


def list_ai_systems(db: Session) -> list[AISystem]:
    return list(db.scalars(select(AISystem).order_by(AISystem.created_at.desc(), AISystem.name.asc())).all())


def get_ai_system(db: Session, system_id: UUID) -> AISystem:
    system = db.get(AISystem, system_id)
    if system is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "AI_SYSTEM_NOT_FOUND"})
    return system


def update_approval_status(db: Session, system_id: UUID, payload: ApprovalStatusUpdate) -> AISystem:
    system = get_ai_system(db, system_id)
    previous_status = system.approval_status
    system.approval_status = payload.approval_status
    db.flush()
    create_audit_event(
        db,
        actor=LOCAL_ACTOR,
        action="ai_system.approval_status_changed",
        entity_type="ai_system",
        entity_id=system.id,
        summary=f"Approval status changed from {previous_status} to {system.approval_status}",
        metadata={
            "previous_status": previous_status,
            "new_status": system.approval_status,
        },
    )
    db.commit()
    db.refresh(system)
    return system
