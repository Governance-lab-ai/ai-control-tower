from sqlalchemy.orm import Session

from app.models import AISystem, AuditEvent
from app.models.base import Base
from app.db.session import engine
from app.services.seed import seed_demo_systems

_ = (AISystem, AuditEvent)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        seed_demo_systems(db)
