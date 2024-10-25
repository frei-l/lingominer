import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from lingominer.base.deps import get_current_user, get_db_session
from lingominer.logger import logger
from lingominer.schemas.integration import MochiConfigCreate, MochiConfig
from lingominer.schemas.mapping import Mapping, MappingField
from lingominer.schemas.card import Language
from lingominer.schemas.user import User

router = APIRouter()



@router.post("/mochi/")
async def add_mochi_mapping(
    data: MochiConfigCreate,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    logger.info(f"add_mochi_mapping: {data}")
    mapping_fields = []
    config_fields = {}
    for mochi_field_id, field in data.fields.items():
        new_field = MappingField(
            name=field["name"],
            source=field["src"],
        )
        mapping_fields.append(new_field)
        config_fields[str(new_field.id)] = mochi_field_id

    mapping = Mapping(
        user_id=user.id,
        lang=data.lang,
        name=data.template_name,
        fields=mapping_fields,
    )
    db_session.add(mapping)
    mochi_config = MochiConfig(
        user_id=user.id,
        api_key=os.getenv("MOCHI_API_KEY"),
        deck_id=data.deck_id,
        template_id=data.template_id,
        template_name=data.template_name,
        fields=config_fields,
        mapping=mapping,
    )
    db_session.add(mochi_config)
    db_session.commit()

    return mochi_config


@router.get("/mochi/")
async def get_mochi_configs(
    lang: Language = Language.English,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    return db_session.exec(
        select(MochiConfig)
        .options(joinedload(MochiConfig.mapping))
        .where(
            MochiConfig.user_id == user.id,
            MochiConfig.mapping.has(Mapping.lang == lang)
        )
    ).all()
