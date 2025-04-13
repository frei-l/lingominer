from typing import Annotated, Optional, Union

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lingominer.api.auth.security import get_current_user
from lingominer.api.mochi.schema import MochiMappingCreate
from lingominer.database import get_db_session
from lingominer.models.mochi import MochiMapping
from lingominer.models.user import User

router = APIRouter()
url = "https://app.mochi.cards/api/templates"


class Fields(BaseModel):
    id: str
    name: str
    type: Optional[str] = None
    options: Optional[dict[str, Union[str, bool]]] = None
    source: Optional[str] = None

    lingominer_field_name: Optional[str] = None
    lingominer_field_id: Optional[str] = None


class MochiTemplate(BaseModel):
    content: str
    fields: dict[str, Fields]
    id: str
    name: str

    lingominer_template_name: Optional[str] = None
    lingominer_template_id: Optional[str] = None


class MochiTemplateList(BaseModel):
    bookmark: str
    docs: list[MochiTemplate]


@router.get("", response_model=MochiTemplateList)
async def get_mochi_templates(
    db_session: Annotated[Session, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
):
    if not user.mochi_api_key:
        raise HTTPException(status_code=400, detail="User has no mochi api key")
    response = requests.get(url, auth=(user.mochi_api_key, ""))
    mochi_templates = MochiTemplateList.model_validate(response.json())

    mochi_mappings = (
        db_session.query(MochiMapping).filter(MochiMapping.user_id == user.id).all()
    )
    for mochi_mapping in mochi_mappings:
        # find first matching template
        matching_template = next(
            (
                t
                for t in mochi_templates.docs
                if t.id == mochi_mapping.mochi_template_id
            ),
            None,
        )
        if matching_template:
            matching_template.lingominer_template_name = (
                mochi_mapping.lingominer_template_name
            )
            matching_template.lingominer_template_id = (
                mochi_mapping.lingominer_template_id
            )

            for field in matching_template.fields.values():
                if field.id in mochi_mapping.mapping:
                    mapping = mochi_mapping.mapping[field.id]
                    field.lingominer_field_name = mapping["name"]
                    field.lingominer_field_id = mapping["id"]

    return mochi_templates


@router.get("/{mochi_template_id}", response_model=MochiTemplate)
async def get_mochi_template(
    db_session: Annotated[Session, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
    mochi_template_id: str,
):
    if not user.mochi_api_key:
        raise HTTPException(status_code=400, detail="User has no mochi api key")
    response = requests.get(f"{url}/{mochi_template_id}", auth=(user.mochi_api_key, ""))
    mochi_template = MochiTemplate.model_validate(response.json())

    mochi_mapping = (
        db_session.query(MochiMapping)
        .filter(MochiMapping.mochi_template_id == mochi_template_id)
        .filter(MochiMapping.user_id == user.id)
        .first()
    )
    if mochi_mapping:
        mochi_template.lingominer_template_name = mochi_mapping.lingominer_template_name
        mochi_template.lingominer_template_id = mochi_mapping.lingominer_template_id
        for field in mochi_template.fields.values():
            if field.id in mochi_mapping.mapping:
                mapping = mochi_mapping.mapping[field.id]
                field.lingominer_field_name = mapping["name"]
                field.lingominer_field_id = mapping["id"]
    return mochi_template


@router.post("/{mochi_template_id}/mapping", response_model=MochiMapping)
async def create_mochi_mapping(
    db_session: Annotated[Session, Depends(get_db_session)],
    mochi_template_id: str,
    mochi_mapping: MochiMappingCreate,
    user: Annotated[User, Depends(get_current_user)],
):
    existing_mochi_mapping = (
        db_session.query(MochiMapping)
        .filter(MochiMapping.mochi_template_id == mochi_template_id)
        .filter(MochiMapping.user_id == user.id)
        .first()
    )

    if existing_mochi_mapping:
        db_session.delete(existing_mochi_mapping)

    mochi_mapping = MochiMapping(
        mochi_template_id=mochi_template_id,
        lingominer_template_id=mochi_mapping.lingominer_template_id,
        lingominer_template_name=mochi_mapping.lingominer_template_name,
        mapping=mochi_mapping.mapping,
        user_id=user.id,
    )

    db_session.add(mochi_mapping)
    db_session.commit()
    db_session.refresh(mochi_mapping)
    return mochi_mapping

@router.delete("/{mochi_template_id}/mapping", response_model=MochiMapping)
async def delete_mochi_mapping(
    db_session: Annotated[Session, Depends(get_db_session)],
    mochi_template_id: str,
    user: Annotated[User, Depends(get_current_user)],
):
    mochi_mapping = (
        db_session.query(MochiMapping)
        .filter(MochiMapping.mochi_template_id == mochi_template_id)
        .filter(MochiMapping.user_id == user.id)
        .first()
    )
    db_session.delete(mochi_mapping)

@router.post("/{mochi_template_id}/cards", response_model=MochiMapping)
async def create_mochi_cards(
    db_session: Annotated[Session, Depends(get_db_session)],
    mochi_template_id: str,
    mochi_mapping: MochiMappingCreate,
    user: Annotated[User, Depends(get_current_user)],
):
    pass
