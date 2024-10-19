import uuid

from sqlmodel import Session, select

from lingominer.schemas.mapping import Mapping, MappingField
from lingominer.schemas.user import User



def get(db_session: Session, user: User):
    stmt = select(Mapping).where(Mapping.user_id == user.id)
    mappings = db_session.exec(stmt).all()
    return mappings


def get_by_id(db_session: Session, mapping_id: uuid.UUID):
    stmt = select(Mapping).where(Mapping.id == mapping_id)
    mapping = db_session.exec(stmt).first()
    return mapping
