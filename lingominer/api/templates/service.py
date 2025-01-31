import uuid

from sqlmodel import Session, select

from lingominer.api.templates.schema import GenerationCreate, TemplateCreate
from lingominer.logger import logger
from lingominer.models.card import CARD_DEFAULT_FIELDS
from lingominer.models.template import Generation, Template, TemplateField

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
    if template is None:
        logger.warning(f"Template {template_id} not found")
        return
    db_session.delete(template)
    db_session.commit()


# Generation


def add_generation(
    db_session: Session, template_id: uuid.UUID, generation_input: GenerationCreate
):
    # validate inputs
    fields_available = db_session.exec(
        select(TemplateField).where(
            TemplateField.name.in_(generation_input.inputs)
            & (TemplateField.template_id == template_id)
        )
    ).all()
    keys_available = set([f.name for f in fields_available])
    keys_required = set(generation_input.inputs) - set(CARD_DEFAULT_FIELDS)
    if keys_available != keys_required:
        missing_keys = keys_required - keys_available
        raise ValueError(f"Some inputs fields are not found: {missing_keys}")

    # create generation
    generation_model = Generation(
        name=generation_input.name,
        template_id=template_id,
        method=generation_input.method,
        prompt=generation_input.prompt,
        inputs=generation_input.inputs,
        outputs=[
            TemplateField(
                name=output.name,
                type=output.type,
                description=output.description,
                template_id=template_id,
            )
            for output in generation_input.outputs
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
    stmt = select(Generation).where(
        Generation.id == generation_id, Generation.template_id == template_id
    )
    generation = db_session.exec(stmt).one_or_none()
    return generation


def delete_generation(
    db_session: Session, template_id: uuid.UUID, generation_id: uuid.UUID
) -> None:
    stmt = select(Generation).where(
        Generation.id == generation_id, Generation.template_id == template_id
    )
    generation = db_session.exec(stmt).one_or_none()
    if generation is None:
        logger.warning(f"Generation {generation_id} not found")
        return

    for field in generation.outputs:
        if field.referenced:
            logger.error(f"field {field.name} is used by other generation")
            return
        db_session.delete(field)
    db_session.delete(generation)
    db_session.commit()
