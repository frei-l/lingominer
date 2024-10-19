import uuid

from sqlmodel import Session, select
from lingominer.schemas.integration import MochiConfig
from lingominer.base.context_var import user_id_var


def get(db_session: Session):
    user_id = user_id_var.get()
    stmt = select(MochiConfig).where(MochiConfig.user_id == user_id)
    configs = db_session.exec(stmt).all()
    return configs


def get_by_id(db_session: Session, config_id: uuid.UUID):
    user_id = user_id_var.get()
    stmt = select(MochiConfig).where(
        MochiConfig.id == config_id and MochiConfig.user_id == user_id
    )
    config = db_session.exec(stmt).first()
    return config
