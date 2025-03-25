import uuid
from typing import Optional

from sqlmodel import Session, select

from lingominer.api.templates.schema import (
    GenerationCreate,
    TemplateCreate,
    GenerationUpdate,
    TemplateFieldCreate,
    TemplateFieldUpdate,
)
from lingominer.logger import logger
from lingominer.config import CARD_DEFAULT_FIELDS
from lingominer.models.template import Generation, Template, TemplateField
from lingominer.models.card import Card
from lingominer.exception import ResourceConflict
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
    # Check if template exists
    stmt = select(Template).where(Template.id == template_id)
    template = db_session.exec(stmt).first()
    if template is None:
        logger.warning(f"Template {template_id} not found")
        return

    # Check if any cards are using this template
    cards_stmt = select(Card).where(Card.template_id == template_id)
    if db_session.exec(cards_stmt).first() is not None:
        raise ResourceConflict(
            f"Cannot delete template {template_id} as it is being used by cards"
        )

    # Delete all GenerationInputFieldLink entries for this template's generations
    for generation in template.generations:
        generation.inputs.clear()

    # Delete all TemplateFields
    for field in template.fields:
        db_session.delete(field)

    # Delete all Generations
    for generation in template.generations:
        db_session.delete(generation)

    # Finally delete the template
    db_session.delete(template)

    # Commit all changes
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
        inputs=fields_available,
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


def update_generation(
    db_session: Session,
    generation_id: uuid.UUID,
    template_id: uuid.UUID,
    generation_update: GenerationUpdate,
) -> Optional[Generation]:
    generation = get_generation(db_session, generation_id, template_id)
    if not generation:
        return None

    update_data = generation_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(generation, key, value)

    db_session.add(generation)
    db_session.commit()
    db_session.refresh(generation)
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


# Template Field


def create_template_field(
    db_session: Session,
    template_id: uuid.UUID,
    field_create: TemplateFieldCreate,
) -> Optional[TemplateField]:
    field = TemplateField(
        name=field_create.name,
        type=field_create.type,
        description=field_create.description,
        template_id=template_id,
        source_id=field_create.generation_id,
    )
    db_session.add(field)
    db_session.commit()
    db_session.refresh(field)
    return field


def get_template_field(
    db_session: Session,
    template_id: uuid.UUID,
    field_id: uuid.UUID,
) -> Optional[TemplateField]:
    stmt = select(TemplateField).where(
        TemplateField.id == field_id,
        TemplateField.template_id == template_id,
    )
    return db_session.exec(stmt).one_or_none()


def update_template_field(
    db_session: Session,
    template_id: uuid.UUID,
    field_id: uuid.UUID,
    field_update: TemplateFieldUpdate,
) -> Optional[TemplateField]:
    field = get_template_field(db_session, template_id, field_id)
    if not field:
        return None

    update_data = field_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(field, key, value)

    db_session.add(field)
    db_session.commit()
    db_session.refresh(field)
    return field


def delete_template_field(
    db_session: Session,
    template_id: uuid.UUID,
    field_id: uuid.UUID,
) -> bool:
    field = get_template_field(db_session, template_id, field_id)
    if not field:
        return False

    if field.referenced:
        logger.error(f"field {field.name} is used by other generation")
        return False

    db_session.delete(field)
    db_session.commit()
    return True
