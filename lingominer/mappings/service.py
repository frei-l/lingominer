import uuid

from sqlmodel import Session, select

from lingominer.schemas.mapping import Mapping, MappingField
from lingominer.schemas.user import User



def get_by_id(db_session: Session, mapping_id: uuid.UUID):
    stmt = select(Mapping).where(Mapping.id == mapping_id)
    mapping = db_session.exec(stmt).first()
    return mapping
