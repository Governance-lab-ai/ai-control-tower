from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.evidence_pack import EvidencePackResponse
from app.schemas.incident import IncidentResponse
from app.schemas.model_run import ModelRunResponse
from app.services.evidence_packs import get_model_run_evidence_pack
from app.services.incidents import list_incidents_for_run
from app.services.model_runs import get_model_run, list_model_runs

router = APIRouter(prefix="/model-runs", tags=["model-runs"])


@router.get("", response_model=list[ModelRunResponse])
def list_runs(db: Session = Depends(get_db)) -> list[ModelRunResponse]:
    return list_model_runs(db)


@router.get("/{run_id}/incidents", response_model=list[IncidentResponse])
def list_run_incidents(run_id: UUID, db: Session = Depends(get_db)) -> list[IncidentResponse]:
    get_model_run(db, run_id)
    return list_incidents_for_run(db, run_id)


@router.get("/{run_id}/evidence-pack", response_model=EvidencePackResponse)
def get_run_evidence_pack(run_id: UUID, db: Session = Depends(get_db)) -> EvidencePackResponse:
    return get_model_run_evidence_pack(db, run_id)


@router.get("/{run_id}", response_model=ModelRunResponse)
def get_run(run_id: UUID, db: Session = Depends(get_db)) -> ModelRunResponse:
    return get_model_run(db, run_id)
