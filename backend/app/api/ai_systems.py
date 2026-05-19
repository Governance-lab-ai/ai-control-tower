from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai_system import AISystemCreate, AISystemResponse, ApprovalStatusUpdate
from app.services.ai_systems import create_ai_system, get_ai_system, list_ai_systems, update_approval_status

router = APIRouter(prefix="/ai-systems", tags=["ai-systems"])


@router.post("", response_model=AISystemResponse, status_code=status.HTTP_201_CREATED)
def create_system(payload: AISystemCreate, db: Session = Depends(get_db)) -> AISystemResponse:
    return create_ai_system(db, payload)


@router.get("", response_model=list[AISystemResponse])
def list_systems(db: Session = Depends(get_db)) -> list[AISystemResponse]:
    return list_ai_systems(db)


@router.get("/{system_id}", response_model=AISystemResponse)
def get_system(system_id: UUID, db: Session = Depends(get_db)) -> AISystemResponse:
    return get_ai_system(db, system_id)


@router.patch("/{system_id}/approval-status", response_model=AISystemResponse)
def patch_approval_status(system_id: UUID, payload: ApprovalStatusUpdate, db: Session = Depends(get_db)) -> AISystemResponse:
    return update_approval_status(db, system_id, payload)
