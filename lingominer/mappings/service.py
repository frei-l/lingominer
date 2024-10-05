import uuid

from sqlmodel import Session, select

from lingominer.schemas.mapping import Mapping, MappingCreate, MappingField
from lingominer.schemas.user import User


def create(db_session: Session, mapping_in: MappingCreate, user: User):
    mapping = Mapping(
        user_id=user.id, lang=mapping_in.lang, name=mapping_in.name, fields=[]
    )
    for field in mapping_in.fields:
        mapping.fields.append(MappingField(**field.model_dump(), mapping_id=mapping.id))
    db_session.add(mapping)
    db_session.commit()
    db_session.refresh(mapping)
    return mapping.id


def get(db_session: Session, user: User):
    stmt = select(Mapping).where(Mapping.user_id == user.id)
    mappings = db_session.exec(stmt).all()
    return mappings


def get_by_id(db_session: Session, mapping_id: uuid.UUID):
    stmt = select(Mapping).where(Mapping.id == mapping_id)
    mapping = db_session.exec(stmt).first()
    return mapping
