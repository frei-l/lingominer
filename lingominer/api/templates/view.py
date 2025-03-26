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
    GenerationUpdate,
    TemplateFieldCreate,
    TemplateFieldResponse,
    TemplateFieldUpdate,
)
from lingominer.database import get_db_session
from lingominer.models.template import Generation
from lingominer.exception import ResourceConflict
from lingominer.api.auth.security import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])

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
    template_id: str,
):
    template = db.get_template(db_session, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/{template_id}")
async def delete_template_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: str,
):
    try:
        db.delete_template(db_session, template_id)
    except ResourceConflict as e:
        raise HTTPException(status_code=409, detail=str(e))


# Generation


@router.post("/{template_id}/generations", response_model=Generation)
async def create_generation_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: str,
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
    template_id: str,
    generation_id: str,
):
    generation = db.get_generation(db_session, generation_id, template_id)
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    return generation


@router.patch(
    "/{template_id}/generations/{generation_id}",
    response_model=GenerationDetailResponse,
)
async def patch_generation_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: str,
    generation_id: str,
    generation_update: GenerationUpdate,
):
    generation = db.update_generation(
        db_session, generation_id, template_id, generation_update
    )
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    return generation


@router.delete("/{template_id}/generations/{generation_id}")
async def delete_generation_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: str,
    generation_id: str,
):
    db.delete_generation(db_session, template_id, generation_id)


# Template Fields


@router.post("/{template_id}/fields", response_model=TemplateFieldResponse)
async def create_template_field_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: str,
    field_create: TemplateFieldCreate,
):
    field = db.create_template_field(db_session, template_id, field_create)
    if not field:
        raise HTTPException(status_code=404, detail="Template not found")
    return field


@router.patch("/{template_id}/fields/{field_id}", response_model=TemplateFieldResponse)
async def update_template_field_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: str,
    field_id: str,
    field_update: TemplateFieldUpdate,
):
    field = db.update_template_field(db_session, template_id, field_id, field_update)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


@router.delete("/{template_id}/fields/{field_id}")
async def delete_template_field_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: str,
    field_id: str,
):
    success = db.delete_template_field(db_session, template_id, field_id)
    if not success:
        raise HTTPException(status_code=404, detail="Field not found or in use")
