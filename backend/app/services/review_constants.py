from app.models.ai_system import AISystem

REVIEW_STATUS_PENDING = "pending"

REVIEW_REASON_PII_INPUT = "pii_detected_input"
REVIEW_REASON_PII_OUTPUT = "pii_detected_output"
REVIEW_REASON_HIGH_RISK_HUMAN_OVERSIGHT = "high_risk_human_oversight"
REVIEW_REASON_HALLUCINATION_FLAG = "hallucination_flag"
REVIEW_REASON_EVALUATION_BELOW_THRESHOLD = "evaluation_below_threshold"

REVIEW_PRIORITY_LOW = "low"
REVIEW_PRIORITY_MEDIUM = "medium"
REVIEW_PRIORITY_HIGH = "high"
REVIEW_PRIORITY_CRITICAL = "critical"


def priority_for_system(ai_system: AISystem) -> str:
    if ai_system.risk_level == "critical":
        return REVIEW_PRIORITY_CRITICAL
    if ai_system.risk_level == "high":
        return REVIEW_PRIORITY_HIGH
    if ai_system.risk_level == "medium":
        return REVIEW_PRIORITY_MEDIUM
    return REVIEW_PRIORITY_LOW
