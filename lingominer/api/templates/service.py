from sqlmodel import Session, select

from lingominer.models.template import Template, Generation, TemplateField
from lingominer.api.templates.schema import TemplateCreate, GenerationCreate
import uuid

# Template

def create_template(db_session: Session, template_create: TemplateCreate):
    template_model = Template(name=template_create.name, lang=template_create.lang)
    db_session.add(template_model)
    db_session.commit()
    db_session.refresh(template_model)
    return template_model

def get_templates(db_session: Session):
    stmt = select(Template)
    templates = db_session.exec(stmt).all()
    return templates

def get_template(db_session: Session, template_id: uuid.UUID):
    stmt = select(Template).where(Template.id == template_id)
    template = db_session.exec(stmt).first()
    return template

def delete_template(db_session: Session, template_id: uuid.UUID):
    stmt = select(Template).where(Template.id == template_id)
    template = db_session.exec(stmt).first()
    db_session.delete(template)
    db_session.commit()

# Generation

def add_generation(
    db_session: Session, template_id: uuid.UUID, generation: GenerationCreate
):
    inputs_fields = db_session.exec(
        select(TemplateField).where(
            TemplateField.name.in_(generation.inputs)
            & (TemplateField.template_id == template_id)
        )
    ).all()
    if len(inputs_fields) != len(generation.inputs):
        raise ValueError("Some inputs fields are not found")

    generation_model = Generation(
        template_id=template_id,
        method=generation.method,
        prompt=generation.prompt,
        inputs=inputs_fields,
        outputs=[
            TemplateField(
                name=output.name, type=output.type, description=output.description
            )
            for output in generation.outputs
        ],
    )
    db_session.add(generation_model)
    db_session.commit()
    db_session.refresh(generation_model)
    return generation_model

def get_generation(
    db_session: Session,
    generation_id: uuid.UUID,
    template_id: uuid.UUID,
):
    stmt = select(Generation).where(Generation.id == generation_id, Generation.template_id == template_id)
    generation = db_session.exec(stmt).first()
    return generation   

def delete_generation(
    db_session: Session,
    template_id: uuid.UUID,
    generation_id: uuid.UUID
) -> None:
    stmt = select(Generation).where(Generation.id == generation_id, Generation.template_id == template_id)
    generation = db_session.exec(stmt).first()
    db_session.delete(generation)
    db_session.commit()
