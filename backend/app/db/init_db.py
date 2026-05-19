from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session

from app.models import AISystem, AuditEvent, Incident, ModelRun, PromptVersion, RetrievedDocument
from app.db.session import engine
from app.services.seed import seed_demo_systems

_ = (AISystem, AuditEvent, Incident, ModelRun, PromptVersion, RetrievedDocument)


def init_db() -> None:
    alembic_cfg = Config("alembic.ini")
    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
    with Session(engine) as db:
        seed_demo_systems(db)
