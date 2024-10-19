import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from lingominer.base.deps import get_current_user, get_db_session
from lingominer.logger import logger
from lingominer.schemas.integration import MochiConfigCreate, MochiConfig
from lingominer.schemas.mapping import Mapping, MappingField
from lingominer.schemas.user import User

router = APIRouter()


# @router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(get_current_user)],
# )
# async def add_mochi_config(
#     config: MochiConfigCreate,
#     db_session: Session = Depends(get_db_session),
# ):
#     config_id = db.create(db_session, config)
#     return {"config_id": config_id}


# @router.get("/", dependencies=[Depends(get_current_user)])
# async def get_mochi_configs_views(
#     db_session: Session = Depends(get_db_session),
# ):
#     configs = db.get(db_session)
#     return {"configs": configs}


# @router.get("/{config_id}", dependencies=[Depends(get_current_user)])
# async def get_mochi_config(
#     config_id: uuid.UUID,
#     db_session: Session = Depends(get_db_session),
# ):
#     config = db.get_by_id(db_session, config_id)
#     if not config:
#         raise HTTPException(status_code=404, detail="Mochi config not found")
#     return config


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
        config_fields[new_field.id] = mochi_field_id

    mapping = Mapping(
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
    )
    db_session.add(mochi_config)
    db_session.commit()

    return mochi_config
