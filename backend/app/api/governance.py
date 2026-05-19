from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.governance import GovernanceRunRequest, GovernanceRunResponse
from app.services.governance_gateway import run_governance_gateway

router = APIRouter(prefix="/governance", tags=["governance"])


@router.post("/run", response_model=GovernanceRunResponse)
def run_gateway(
    payload: GovernanceRunRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> GovernanceRunResponse:
    return run_governance_gateway(db, settings, payload)
