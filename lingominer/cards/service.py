import uuid

from sqlmodel import Session, select

from lingominer.schemas.card import Card, CardBase, CardStatus
from lingominer.schemas.user import User


def create(db_session: Session, card: CardBase, user: User):
    card_from_user = Card(user_id=user.id, **card.model_dump())
    db_session.add(card_from_user)
    db_session.commit()
    db_session.refresh(card_from_user)
    return card_from_user


def get(db_session: Session, user: User):
    stmt = select(Card).where(Card.user_id == user.id and Card.status == CardStatus.NEW)
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
