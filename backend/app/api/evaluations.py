from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.evaluation import EvaluationResponse
from app.services.evaluations import get_evaluation, list_evaluations

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("", response_model=list[EvaluationResponse])
def list_evaluation_records(
    failed_only: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[EvaluationResponse]:
    return list_evaluations(db, failed_only=failed_only)


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation_record(evaluation_id: UUID, db: Session = Depends(get_db)) -> EvaluationResponse:
    return get_evaluation(db, evaluation_id)
