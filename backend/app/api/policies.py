from fastapi import APIRouter, HTTPException, status

from app.schemas.policy import PolicyDecisionResponse, PolicyEvaluationRequest
from app.services.policy_engine import evaluate_policy_request

router = APIRouter(prefix="/policies", tags=["policies"])


@router.post("/evaluate", response_model=PolicyDecisionResponse)
def evaluate_policy(payload: PolicyEvaluationRequest) -> PolicyDecisionResponse:
    try:
        return evaluate_policy_request(action_type=payload.action_type, actor=payload.actor, context=payload.context)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"code": "UNSUPPORTED_POLICY_ACTION", "message": str(exc)}) from exc
