from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_system import AISystem
from app.models.evaluation import Evaluation
from app.models.human_review import HumanReview
from app.models.incident import Incident
from app.models.model_run import ModelRun
from app.schemas.dashboard import DashboardSummaryResponse, ModelUsageSummary, RiskHeatmapCell

RISK_LEVELS = ("low", "medium", "high", "critical")
ACTIVE_INCIDENT_STATUSES = ("open", "under_review")


def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    total_ai_systems = _count(db, AISystem)
    total_runs = _count(db, ModelRun)
    pending_reviews = _scalar_count(db, select(func.count()).select_from(HumanReview).where(HumanReview.status == "pending"))
    open_incidents = _scalar_count(
        db,
        select(func.count()).select_from(Incident).where(Incident.status.in_(ACTIVE_INCIDENT_STATUSES)),
    )
    failed_evaluations = _scalar_count(
        db,
        select(func.count()).select_from(Evaluation).where(Evaluation.requires_human_review.is_(True)),
    )
    total_cost_usd = float(db.scalar(select(func.coalesce(func.sum(ModelRun.cost_usd), 0))) or 0)
    average_latency_ms = float(db.scalar(select(func.coalesce(func.avg(ModelRun.latency_ms), 0))) or 0)

    return DashboardSummaryResponse(
        total_ai_systems=total_ai_systems,
        systems_by_risk=_systems_by_risk(db),
        systems_by_department=_group_counts(db, AISystem.department),
        pending_reviews=pending_reviews,
        open_incidents=open_incidents,
        failed_evaluations=failed_evaluations,
        total_runs=total_runs,
        total_cost_usd=round(total_cost_usd, 6),
        average_latency_ms=round(average_latency_ms, 2),
        risk_heatmap=_risk_heatmap(db),
        incidents_by_severity=_group_counts(
            db,
            Incident.severity,
            Incident.status.in_(ACTIVE_INCIDENT_STATUSES),
        ),
        incidents_by_type=_group_counts(
            db,
            Incident.incident_type,
            Incident.status.in_(ACTIVE_INCIDENT_STATUSES),
        ),
        usage_by_model=_usage_by_model(db),
        recent_incidents=list(
            db.scalars(
                select(Incident)
                .where(Incident.status.in_(ACTIVE_INCIDENT_STATUSES))
                .order_by(Incident.created_at.desc())
                .limit(5)
            ).all()
        ),
        recent_failed_evaluations=list(
            db.scalars(
                select(Evaluation)
                .where(Evaluation.requires_human_review.is_(True))
                .order_by(Evaluation.created_at.desc())
                .limit(5)
            ).all()
        ),
    )


def _count(db: Session, model: type) -> int:
    return _scalar_count(db, select(func.count()).select_from(model))


def _scalar_count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)


def _systems_by_risk(db: Session) -> dict[str, int]:
    counts = {risk_level: 0 for risk_level in RISK_LEVELS}
    counts.update(_group_counts(db, AISystem.risk_level))
    return counts


def _group_counts(db: Session, column, *where_clauses) -> dict[str, int]:
    statement = select(column, func.count()).group_by(column)
    for clause in where_clauses:
        statement = statement.where(clause)
    return {str(key): int(count) for key, count in db.execute(statement).all()}


def _risk_heatmap(db: Session) -> list[RiskHeatmapCell]:
    rows = db.execute(
        select(AISystem.department, AISystem.risk_level, func.count())
        .group_by(AISystem.department, AISystem.risk_level)
        .order_by(AISystem.department, AISystem.risk_level)
    ).all()
    return [RiskHeatmapCell(department=department, risk_level=risk_level, count=int(count)) for department, risk_level, count in rows]


def _usage_by_model(db: Session) -> list[ModelUsageSummary]:
    rows = db.execute(
        select(
            ModelRun.model_provider,
            ModelRun.model_name,
            func.count(),
            func.coalesce(func.sum(ModelRun.cost_usd), 0),
            func.coalesce(func.avg(ModelRun.latency_ms), 0),
        )
        .group_by(ModelRun.model_provider, ModelRun.model_name)
        .order_by(func.count().desc())
    ).all()
    return [
        ModelUsageSummary(
            model_provider=model_provider,
            model_name=model_name,
            total_runs=int(total_runs),
            total_cost_usd=round(float(total_cost_usd or 0), 6),
            average_latency_ms=round(float(average_latency_ms or 0), 2),
        )
        for model_provider, model_name, total_runs, total_cost_usd, average_latency_ms in rows
    ]
