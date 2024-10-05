import uuid

from sqlmodel import Session, select

from lingominer.schemas.integration import MochiConfig, MochiConfigCreate


def create(db_session: Session, mochi_config: MochiConfigCreate):
    db_mochi_config = MochiConfig(**mochi_config.model_dump())
    db_session.add(db_mochi_config)
    db_session.commit()
    db_session.refresh(db_mochi_config)
    return db_mochi_config.id


def get_by_id(db_session: Session, config_id: uuid.UUID):
    stmt = select(MochiConfig).where(MochiConfig.id == config_id)
    mochi_config = db_session.exec(stmt).first()
    return mochi_config


def get(db_session: Session):
    stmt = select(MochiConfig)
    mochi_configs = db_session.exec(stmt).all()
    return mochi_configs
