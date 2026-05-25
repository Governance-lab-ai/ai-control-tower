from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.audit_event import AuditEventResponse
from app.services.audit import audit_events_to_csv, export_audit_events

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/export")
def export_audit(
    format: Literal["csv", "json"] = "csv",
    system_id: UUID | None = None,
    department: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    risk_level: Literal["low", "medium", "high", "critical"] | None = None,
    incident_type: str | None = None,
    limit: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    events = export_audit_events(
        db,
        system_id=system_id,
        department=department,
        start_date=start_date,
        end_date=end_date,
        risk_level=risk_level,
        incident_type=incident_type,
        limit=limit,
    )
    if format == "json":
        return [AuditEventResponse.model_validate(event) for event in events]

    return Response(
        content=audit_events_to_csv(events),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="audit-export.csv"'},
    )
