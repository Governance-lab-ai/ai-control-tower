from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.ai_system import AISystem
from app.models.prompt_version import PromptVersion
from app.schemas.prompt_version import PromptVersionCreate
from app.services.audit import create_audit_event

LOCAL_ACTOR = "local_mock:governance_admin"
DEFAULT_PROMPT_TEXT = "Use the registered AI system purpose and approved governance policy when responding."


def ensure_default_prompt_version(db: Session, ai_system: AISystem) -> PromptVersion:
    active = get_active_prompt_version(db, ai_system.id)
    if active is not None:
        return active

    prompt_version = PromptVersion(
        ai_system_id=ai_system.id,
        version="v1",
        name=f"{ai_system.name} default prompt",
        prompt_text=DEFAULT_PROMPT_TEXT,
        status="active",
    )
    db.add(prompt_version)
    db.flush()
    return prompt_version


def get_active_prompt_version(db: Session, system_id: UUID) -> PromptVersion | None:
    statement = (
        select(PromptVersion)
        .where(PromptVersion.ai_system_id == system_id, PromptVersion.status == "active")
        .order_by(PromptVersion.created_at.desc())
    )
    return db.scalars(statement).first()


def list_prompt_versions(db: Session, system_id: UUID) -> list[PromptVersion]:
    _get_system_or_404(db, system_id)
    statement = select(PromptVersion).where(PromptVersion.ai_system_id == system_id).order_by(PromptVersion.created_at.desc())
    return list(db.scalars(statement).all())


def create_prompt_version(db: Session, system_id: UUID, payload: PromptVersionCreate) -> PromptVersion:
    system = _get_system_or_404(db, system_id)
    version = payload.version or _next_version_label(db, system_id)
    _raise_if_duplicate_version(db, system_id, version)

    if payload.status == "active":
        _retire_active_versions(db, system_id)

    prompt_version = PromptVersion(
        ai_system_id=system.id,
        version=version,
        name=payload.name,
        prompt_text=payload.prompt_text,
        status=payload.status,
    )
    db.add(prompt_version)
    db.flush()
    create_audit_event(
        db,
        actor=LOCAL_ACTOR,
        action="prompt_version.created",
        entity_type="prompt_version",
        entity_id=prompt_version.id,
        summary=f"Prompt version created for {system.name}: {prompt_version.version}",
        metadata={"ai_system_id": str(system.id), "status": prompt_version.status},
    )
    db.commit()
    db.refresh(prompt_version)
    return prompt_version


def approve_prompt_version(db: Session, prompt_version_id: UUID) -> PromptVersion:
    prompt_version = _get_prompt_version_or_404(db, prompt_version_id)
    if prompt_version.status not in {"draft", "approved"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "PROMPT_VERSION_STATUS_INVALID", "message": "Only draft prompt versions can be approved."},
        )

    prompt_version.status = "approved"
    db.flush()
    create_audit_event(
        db,
        actor=LOCAL_ACTOR,
        action="prompt_version.approved",
        entity_type="prompt_version",
        entity_id=prompt_version.id,
        summary=f"Prompt version approved: {prompt_version.version}",
        metadata={"ai_system_id": str(prompt_version.ai_system_id)},
    )
    db.commit()
    db.refresh(prompt_version)
    return prompt_version


def activate_prompt_version(db: Session, prompt_version_id: UUID) -> PromptVersion:
    prompt_version = _get_prompt_version_or_404(db, prompt_version_id)
    if prompt_version.status not in {"approved", "active"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "PROMPT_VERSION_NOT_APPROVED", "message": "Prompt versions must be approved before activation."},
        )

    _retire_active_versions(db, prompt_version.ai_system_id)
    prompt_version.status = "active"
    db.flush()
    create_audit_event(
        db,
        actor=LOCAL_ACTOR,
        action="prompt_version.activated",
        entity_type="prompt_version",
        entity_id=prompt_version.id,
        summary=f"Prompt version activated: {prompt_version.version}",
        metadata={"ai_system_id": str(prompt_version.ai_system_id)},
    )
    db.commit()
    db.refresh(prompt_version)
    return prompt_version


def retire_prompt_version(db: Session, prompt_version_id: UUID) -> PromptVersion:
    prompt_version = _get_prompt_version_or_404(db, prompt_version_id)
    if prompt_version.status == "retired":
        return prompt_version

    prompt_version.status = "retired"
    db.flush()
    create_audit_event(
        db,
        actor=LOCAL_ACTOR,
        action="prompt_version.retired",
        entity_type="prompt_version",
        entity_id=prompt_version.id,
        summary=f"Prompt version retired: {prompt_version.version}",
        metadata={"ai_system_id": str(prompt_version.ai_system_id)},
    )
    db.commit()
    db.refresh(prompt_version)
    return prompt_version


def _get_system_or_404(db: Session, system_id: UUID) -> AISystem:
    system = db.get(AISystem, system_id)
    if system is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "AI_SYSTEM_NOT_FOUND"})
    return system


def _get_prompt_version_or_404(db: Session, prompt_version_id: UUID) -> PromptVersion:
    prompt_version = db.get(PromptVersion, prompt_version_id)
    if prompt_version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "PROMPT_VERSION_NOT_FOUND"})
    return prompt_version


def _retire_active_versions(db: Session, system_id: UUID) -> None:
    db.execute(
        update(PromptVersion)
        .where(PromptVersion.ai_system_id == system_id, PromptVersion.status == "active")
        .values(status="retired")
    )


def _next_version_label(db: Session, system_id: UUID) -> str:
    existing_count = db.scalar(select(func.count(PromptVersion.id)).where(PromptVersion.ai_system_id == system_id)) or 0
    return f"v{existing_count + 1}"


def _raise_if_duplicate_version(db: Session, system_id: UUID, version: str) -> None:
    existing = db.scalar(select(PromptVersion.id).where(PromptVersion.ai_system_id == system_id, PromptVersion.version == version))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "PROMPT_VERSION_ALREADY_EXISTS", "message": "Prompt version labels must be unique per AI system."},
        )
