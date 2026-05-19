from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.prompt_version import PromptVersionCreate, PromptVersionResponse
from app.services.prompt_versions import activate_prompt_version, create_prompt_version, list_prompt_versions

router = APIRouter(tags=["prompt-versions"])


@router.get("/ai-systems/{system_id}/prompt-versions", response_model=list[PromptVersionResponse])
def list_system_prompt_versions(system_id: UUID, db: Session = Depends(get_db)) -> list[PromptVersionResponse]:
    return list_prompt_versions(db, system_id)


@router.post("/ai-systems/{system_id}/prompt-versions", response_model=PromptVersionResponse, status_code=status.HTTP_201_CREATED)
def create_system_prompt_version(
    system_id: UUID,
    payload: PromptVersionCreate,
    db: Session = Depends(get_db),
) -> PromptVersionResponse:
    return create_prompt_version(db, system_id, payload)


@router.patch("/prompt-versions/{prompt_version_id}/activate", response_model=PromptVersionResponse)
def patch_activate_prompt_version(prompt_version_id: UUID, db: Session = Depends(get_db)) -> PromptVersionResponse:
    return activate_prompt_version(db, prompt_version_id)
