from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.incident import IncidentResponse, IncidentUpdateRequest
from app.services.incidents import get_incident, list_incidents, update_incident_status

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentResponse])
def list_all_incidents(db: Session = Depends(get_db)) -> list[IncidentResponse]:
    return list_incidents(db)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_detail(incident_id: UUID, db: Session = Depends(get_db)) -> IncidentResponse:
    return get_incident(db, incident_id)


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: UUID,
    payload: IncidentUpdateRequest,
    db: Session = Depends(get_db),
) -> IncidentResponse:
    return update_incident_status(
        db,
        incident_id=incident_id,
        status_=payload.status,
        actor=payload.actor,
        notes=payload.notes,
    )
