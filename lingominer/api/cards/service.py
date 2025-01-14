import uuid

from sqlmodel import Session, select

from lingominer.models.card import Card
from lingominer.api.cards.schema import CardCreate, CardUpdate


def create(
    db_session: Session, card_create: CardCreate, template_id: uuid.UUID, content: dict
):
    card_from_template = Card(
        template_id=template_id, **card_create.model_dump(), content=content
    )
    db_session.add(card_from_template)
    db_session.commit()
    db_session.refresh(card_from_template)
    return card_from_template


def get(db_session: Session, template_id: uuid.UUID):
    stmt = select(Card).where(Card.template_id == template_id)
    cards = db_session.exec(stmt).all()
    return cards


def get_by_id(db_session: Session, card_id: uuid.UUID):
    stmt = select(Card).where(Card.id == card_id)
    card = db_session.exec(stmt).first()
    return card


def delete(db_session: Session, card_id: uuid.UUID):
    stmt = select(Card).where(Card.id == card_id)
    card = db_session.exec(stmt).first()
    db_session.delete(card)
    db_session.commit()

def update(db_session: Session, card_id: uuid.UUID, card_update: CardUpdate):
    stmt = select(Card).where(Card.id == card_id)
    card = db_session.exec(stmt).first()
    card.update(card_update.model_dump())
    db_session.commit()
    db_session.refresh(card)
    return card
