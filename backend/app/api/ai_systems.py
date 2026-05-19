from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai_system import AISystemCreate, AISystemResponse, ApprovalStatusUpdate
from app.schemas.incident import IncidentResponse
from app.schemas.model_run import ModelRunResponse
from app.services.ai_systems import create_ai_system, get_ai_system, list_ai_systems, update_approval_status
from app.services.incidents import list_incidents_for_system
from app.services.model_runs import list_model_runs_for_system

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


@router.get("/{system_id}/runs", response_model=list[ModelRunResponse])
def list_system_runs(system_id: UUID, db: Session = Depends(get_db)) -> list[ModelRunResponse]:
    return list_model_runs_for_system(db, system_id)


@router.get("/{system_id}/incidents", response_model=list[IncidentResponse])
def list_system_incidents(system_id: UUID, db: Session = Depends(get_db)) -> list[IncidentResponse]:
    return list_incidents_for_system(db, system_id)


@router.patch("/{system_id}/approval-status", response_model=AISystemResponse)
def patch_approval_status(system_id: UUID, payload: ApprovalStatusUpdate, db: Session = Depends(get_db)) -> AISystemResponse:
    return update_approval_status(db, system_id, payload)
