from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AISystem, AuditEvent, Evaluation, HumanReview, Incident, ModelRun, PromptVersion, RetrievedDocument, RunStep
from app.db.session import engine
from app.services.seed import ensure_default_prompt_versions, seed_demo_systems

_ = (AISystem, AuditEvent, Evaluation, HumanReview, Incident, ModelRun, PromptVersion, RetrievedDocument, RunStep)


def init_db() -> None:
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
    with Session(engine) as db:
        if settings.enable_demo_seed:
            seed_demo_systems(db)
        else:
            ensure_default_prompt_versions(db)
