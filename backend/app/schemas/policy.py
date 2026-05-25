from typing import Literal

from pydantic import BaseModel, Field

PolicyDecisionAction = Literal["allow", "deny", "require_review"]


class PolicyDecisionResponse(BaseModel):
    policy_name: str
    policy_version: str
    action: PolicyDecisionAction
    reasons: list[str]
    matched_rules: list[str]
    metadata: dict = Field(default_factory=dict)


class PolicyEvaluationRequest(BaseModel):
    action_type: Literal["model_execution", "tool_call"]
    actor: str = Field(min_length=2, max_length=160)
    context: dict = Field(default_factory=dict)
