import uuid
from lingominer.api.templates.service import (
    get_template,
    create_template,
    delete_template,
    add_generation,
    delete_generation,
    get_generation,
)
from lingominer.api.templates.schema import (
    TemplateCreate,
    GenerationCreate,
)
from lingominer.models.template import Template, Generation
from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

# Template

@router.post("/templates", response_model=Template)
async def create_template_view(db_session: Session, template_create: TemplateCreate):
    template = create_template(db_session, template_create)
    return template

@router.get("/templates", response_model=list[Template])
async def get_templates(db_session: Session):
    templates = get_templates(db_session)
    return templates

@router.get("/templates/{template_id}", response_model=Template)
async def get_template_view(db_session: Session, template_id: uuid.UUID):
    template = get_template(db_session, template_id)
    return template

@router.delete("/templates/{template_id}")
async def delete_template_view(db_session: Session, template_id: uuid.UUID):
    delete_template(db_session, template_id)
    

# Generation


@router.post("/templates/{template_id}/generations", response_model=Generation)
async def create_generation_view(
    db_session: Session, template_id: uuid.UUID, generation_create: GenerationCreate
):
    generation = add_generation(db_session, template_id, generation_create)
    return generation

@router.get("/templates/{template_id}/generations/{generation_id}", response_model=Generation)
async def get_generation_view(db_session: Session, template_id: uuid.UUID, generation_id: uuid.UUID):
    generation = get_generation(db_session, generation_id, template_id)
    return generation

@router.delete("/templates/{template_id}/generations/{generation_id}")
async def delete_generation_view(db_session: Session, template_id: uuid.UUID, generation_id: uuid.UUID):
    delete_generation(db_session, template_id, generation_id)