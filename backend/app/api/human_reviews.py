from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.human_review import HumanReviewDecisionRequest, HumanReviewDetailResponse, HumanReviewResponse
from app.services.human_reviews import decide_review, get_review, list_reviews

router = APIRouter(prefix="/reviews", tags=["human-reviews"])


@router.get("", response_model=list[HumanReviewResponse])
def list_human_reviews(
    status: str | None = Query(default="pending"),
    db: Session = Depends(get_db),
) -> list[HumanReviewResponse]:
    return list_reviews(db, status_filter=status)


@router.get("/{review_id}", response_model=HumanReviewDetailResponse)
def get_human_review(review_id: UUID, db: Session = Depends(get_db)) -> HumanReviewDetailResponse:
    return get_review(db, review_id)


@router.post("/{review_id}/decision", response_model=HumanReviewDetailResponse)
def post_human_review_decision(
    review_id: UUID,
    payload: HumanReviewDecisionRequest,
    db: Session = Depends(get_db),
) -> HumanReviewDetailResponse:
    return decide_review(db, review_id=review_id, payload=payload)
