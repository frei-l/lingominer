from lingominer.logger import logger
from lingominer.schemas.user import User
from lingominer.schemas.card import CardBase, Card, CardStatus
from lingominer.schemas.mapping import (
    Mapping,
    MappingCreate,
    MappingField,
)
from lingominer.schemas.integration import MochiConfig, MochiConfigCreate
from sqlmodel import Session, select

from secrets import token_urlsafe
from hashlib import sha256
import os
import uuid

def create_user(db_session: Session, username: str):
    token = "sk_" + token_urlsafe(16)
    # hash token use passlib
    user = User(username=username, hash_token=sha256(token.encode()).hexdigest())
    db_session.add(user)
    db_session.commit()
    return token


def verify_user(db_session: Session, token: str):
    if os.getenv("DEV") and not token:
        token = os.getenv("DEV_API_KEY")
    logger.info(f"verify user: {token}")
    stmt = select(User).where(User.hash_token == sha256(token.encode()).hexdigest())
    user = db_session.exec(stmt).first()
    logger.info(f"user: {user}")
    if user:
        return user
    return None


def save_card(db_session: Session, card: CardBase, user: User):
    card_from_user = Card(user_id=user.id, **card.model_dump())
    db_session.add(card_from_user)
    db_session.commit()
    db_session.refresh(card_from_user)
    return card_from_user.id


def get_cards(db_session: Session, user: User):
    stmt = select(Card).where(
        Card.user_id == user.id and Card.status == CardStatus.NEW
    )
    cards = db_session.exec(stmt).all()
    return cards

def get_card_by_id(db_session: Session, card_id: uuid.UUID):
    stmt = select(Card).where(Card.id == card_id)
    card = db_session.exec(stmt).first()
    return card


def save_mapping(db_session: Session, mapping_in: MappingCreate, user: User):
    mapping = Mapping(
        user_id=user.id, lang=mapping_in.lang, name=mapping_in.name, fields=[]
    )
    for field in mapping_in.fields:
        mapping.fields.append(
            MappingField(**field.model_dump(), mapping_id=mapping.id)
        )
    db_session.add(mapping)
    db_session.commit()
    db_session.refresh(mapping)
    return mapping.id


def get_mappings(db_session: Session, user: User):
    stmt = select(Mapping).where(Mapping.user_id == user.id)
    mappings = db_session.exec(stmt).all()
    return mappings

def get_mapping_by_id(db_session: Session, mapping_id: uuid.UUID):
    stmt = select(Mapping).where(Mapping.id == mapping_id)
    mapping = db_session.exec(stmt).first()
    return mapping

def create_mochi_config(db_session: Session, mochi_config: MochiConfigCreate):
    db_mochi_config = MochiConfig(**mochi_config.model_dump())
    db_session.add(db_mochi_config)
    db_session.commit()
    db_session.refresh(db_mochi_config)
    return db_mochi_config.id

def get_mochi_config_by_id(db_session: Session, config_id: uuid.UUID):
    stmt = select(MochiConfig).where(MochiConfig.id == config_id)
    mochi_config = db_session.exec(stmt).first()
    return mochi_config

def get_mochi_configs(db_session: Session):
    stmt = select(MochiConfig)
    mochi_configs = db_session.exec(stmt).all()
    return mochi_configs
