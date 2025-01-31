import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from lingominer.api.templates import service as db
from lingominer.api.templates.schema import (
    GenerationCreate,
    GenerationDetailResponse,
    TemplateCreate,
    TemplateDetailResponse,
    TemplateResponse,
)
from lingominer.database import get_db_session
from lingominer.models.template import Generation

router = APIRouter()

# Template


@router.post("", response_model=TemplateDetailResponse)
async def create_template_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_create: TemplateCreate,
):
    template = db.create_template(db_session, template_create)
    return template


@router.get("", response_model=list[TemplateResponse])
async def get_templates(
    db_session: Annotated[Session, Depends(get_db_session)],
):
    templates = db.get_templates(db_session)
    return templates


@router.get("/{template_id}", response_model=TemplateDetailResponse)
async def get_template_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: uuid.UUID,
):
    template = db.get_template(db_session, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/{template_id}")
async def delete_template_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: uuid.UUID,
):
    db.delete_template(db_session, template_id)


# Generation


@router.post("/{template_id}/generations", response_model=Generation)
async def create_generation_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: uuid.UUID,
    generation_create: GenerationCreate,
):
    generation = db.add_generation(db_session, template_id, generation_create)
    return generation


@router.get(
    "/{template_id}/generations/{generation_id}",
    response_model=GenerationDetailResponse,
)
async def get_generation_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: uuid.UUID,
    generation_id: uuid.UUID,
):
    generation = db.get_generation(db_session, generation_id, template_id)
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    return generation


@router.delete("/{template_id}/generations/{generation_id}")
async def delete_generation_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: uuid.UUID,
    generation_id: uuid.UUID,
):
    db.delete_generation(db_session, template_id, generation_id)
