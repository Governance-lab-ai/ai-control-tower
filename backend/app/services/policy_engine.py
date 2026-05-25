from dataclasses import dataclass, field

from app.models.ai_system import AISystem
from app.schemas.governance import GovernanceRunRequest
from app.schemas.policy import PolicyDecisionResponse
from app.services.pii import PIIResult

LOCAL_POLICY_NAME = "local-governance-policy"
LOCAL_POLICY_VERSION = "2026.05.local-v1"


@dataclass(frozen=True)
class PolicyDecision:
    policy_name: str
    policy_version: str
    action: str
    reasons: list[str]
    matched_rules: list[str]
    metadata: dict = field(default_factory=dict)

    def to_response(self) -> PolicyDecisionResponse:
        return PolicyDecisionResponse(
            policy_name=self.policy_name,
            policy_version=self.policy_version,
            action=self.action,  # type: ignore[arg-type]
            reasons=self.reasons,
            matched_rules=self.matched_rules,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict:
        return self.to_response().model_dump()


def evaluate_model_execution_policy(
    *,
    ai_system: AISystem,
    payload: GovernanceRunRequest,
    input_pii_result: PIIResult,
) -> PolicyDecision:
    matched_rules: list[str] = []
    reasons: list[str] = []
    action = "allow"

    if ai_system.approval_status in {"blocked", "retired"}:
        matched_rules.append("block-unapproved-or-retired-system")
        reasons.append(f"AI system approval status is {ai_system.approval_status}.")
        action = "deny"
    elif ai_system.approval_status == "pending":
        matched_rules.append("review-pending-system")
        reasons.append("AI system is pending approval.")
        action = "require_review"
    else:
        matched_rules.append("allow-approved-system")
        reasons.append("AI system is approved for model execution.")

    if input_pii_result.pii_detected:
        matched_rules.append("flag-input-pii")
        reasons.append(f"Input PII detected: {', '.join(input_pii_result.pii_types)}.")

    return PolicyDecision(
        policy_name=LOCAL_POLICY_NAME,
        policy_version=LOCAL_POLICY_VERSION,
        action=action,
        reasons=reasons,
        matched_rules=matched_rules,
        metadata={
            "action_type": "model_execution",
            "actor": payload.actor,
            "ai_system_id": str(ai_system.id),
            "approval_status": ai_system.approval_status,
            "risk_level": ai_system.risk_level,
            "contains_personal_data": ai_system.contains_personal_data,
            "human_oversight_required": ai_system.human_oversight_required,
            "input_pii_detected": input_pii_result.pii_detected,
            "metadata": payload.metadata,
        },
    )


def evaluate_tool_call_policy(*, actor: str, context: dict) -> PolicyDecision:
    tool_name = str(context.get("tool_name", "")).strip()
    action_type = str(context.get("action", "")).strip().lower()
    allowed_tools = set(context.get("allowed_tools") or [])

    matched_rules: list[str] = []
    reasons: list[str] = []
    action = "allow"

    destructive_actions = {"delete", "drop", "truncate", "execute_shell", "write_file"}
    high_impact_tools = {"send_email", "database_write", "payment_action", "external_api_write"}

    if not tool_name:
        matched_rules.append("deny-missing-tool-name")
        reasons.append("Tool call did not include a tool_name.")
        action = "deny"
    elif allowed_tools and tool_name not in allowed_tools:
        matched_rules.append("deny-tool-not-granted")
        reasons.append(f"Tool {tool_name} is not in the granted tool allowlist.")
        action = "deny"
    elif action_type in destructive_actions or tool_name in {"shell_exec", "delete_file", "drop_table"}:
        matched_rules.append("deny-destructive-tool-action")
        reasons.append("Destructive tool actions are blocked by the local policy.")
        action = "deny"
    elif tool_name in high_impact_tools:
        matched_rules.append("review-high-impact-tool")
        reasons.append(f"Tool {tool_name} requires human review before execution.")
        action = "require_review"
    else:
        matched_rules.append("allow-low-impact-tool")
        reasons.append(f"Tool {tool_name} is allowed by the local policy.")

    return PolicyDecision(
        policy_name=LOCAL_POLICY_NAME,
        policy_version=LOCAL_POLICY_VERSION,
        action=action,
        reasons=reasons,
        matched_rules=matched_rules,
        metadata={
            "action_type": "tool_call",
            "actor": actor,
            "tool_name": tool_name,
            "tool_action": action_type,
            "allowed_tools": sorted(allowed_tools),
        },
    )


def evaluate_policy_request(*, action_type: str, actor: str, context: dict) -> PolicyDecisionResponse:
    if action_type == "tool_call":
        return evaluate_tool_call_policy(actor=actor, context=context).to_response()
    if action_type == "model_execution":
        approval_status = str(context.get("approval_status", "pending"))
        risk_level = str(context.get("risk_level", "medium"))
        input_pii_detected = bool(context.get("input_pii_detected", False))
        action = "allow"
        matched_rules = ["allow-approved-system"]
        reasons = ["AI system is approved for model execution."]
        if approval_status in {"blocked", "retired"}:
            action = "deny"
            matched_rules = ["block-unapproved-or-retired-system"]
            reasons = [f"AI system approval status is {approval_status}."]
        elif approval_status == "pending":
            action = "require_review"
            matched_rules = ["review-pending-system"]
            reasons = ["AI system is pending approval."]
        if input_pii_detected:
            matched_rules.append("flag-input-pii")
            reasons.append("Input PII was supplied in the policy context.")
        return PolicyDecision(
            policy_name=LOCAL_POLICY_NAME,
            policy_version=LOCAL_POLICY_VERSION,
            action=action,
            reasons=reasons,
            matched_rules=matched_rules,
            metadata={"action_type": "model_execution", "actor": actor, **context},
        ).to_response()
    raise ValueError(f"Unsupported policy action_type: {action_type}")
