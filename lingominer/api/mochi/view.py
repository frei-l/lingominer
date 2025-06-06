from typing import Annotated, Optional, TypedDict, Union

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from lingominer.api.auth.security import get_current_user
from lingominer.api.mochi.schema import (
    MappingField,
    MochiDeckMapping,
    MochiDeckMappingItem,
    MochiMappingCreate,
)
from lingominer.database import get_db_session
from lingominer.models.card import Card
from lingominer.models.mochi import MochiMapping
from lingominer.models.user import User

router = APIRouter()
base_url = "https://app.mochi.cards/api"


class MochiField(TypedDict):
    id: str
    name: str
    type: Optional[str] = None
    options: Optional[dict[str, Union[str, bool]]] = None
    source: Optional[str] = None


class MochiTemplate(TypedDict):
    name: str
    content: str
    fields: dict[str, MochiField]
    id: str


MochiDeck = TypedDict("MochiDeck", {"id": str, "name": str, "template-id": str})


class MochiDeckList(TypedDict):
    bookmark: str
    docs: list[MochiDeck]


@router.get("", response_model=list[MochiDeckMappingItem])
async def get_mochi_deck_mappings(
    db_session: Annotated[Session, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
    lm_template_id: Optional[str] = None,
):
    if not user.mochi_api_key:
        raise HTTPException(status_code=400, detail="User has no mochi api key")

    mochi_decks: MochiDeckList = requests.get(
        base_url + "/decks", auth=(user.mochi_api_key, "")
    ).json()
    if lm_template_id:
        mochi_mappings = (
            db_session.query(MochiMapping)
            .filter(MochiMapping.user_id == user.id)
            .filter(MochiMapping.lingominer_template_id == lm_template_id)
            .all()
        )
    else:
        mochi_mappings = (
            db_session.query(MochiMapping).filter(MochiMapping.user_id == user.id).all()
        )

    deck_items = [
        MochiDeckMappingItem(
            id=i["id"],
            name=i["name"],
            template_id=i["template-id"],
        )
        for i in mochi_decks["docs"]
    ]
    for mochi_mapping in mochi_mappings:
        matched_deck = next(
            (t for t in deck_items if t.id == mochi_mapping.mochi_deck_id),
            None,
        )
        if matched_deck:
            matched_deck.lingominer_template_name = (
                mochi_mapping.lingominer_template_name
            )
            matched_deck.lingominer_template_id = mochi_mapping.lingominer_template_id

    return deck_items


@router.get("/{mochi_deck_id}", response_model=MochiDeckMapping)
async def get_mochi_deck_mapping(
    db_session: Annotated[Session, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
    mochi_deck_id: str,
):
    if not user.mochi_api_key:
        raise HTTPException(status_code=400, detail="User has no mochi api key")
    deck_info: MochiDeck = requests.get(
        f"{base_url}/decks/{mochi_deck_id}", auth=(user.mochi_api_key, "")
    ).json()
    template_info: MochiTemplate = requests.get(
        f"{base_url}/templates/{deck_info['template-id']}",
        auth=(user.mochi_api_key, ""),
    ).json()
    deck_mapping = MochiDeckMapping(
        id=deck_info["id"],
        name=deck_info["name"],
        template_id=deck_info["template-id"],
        template_name=template_info["name"],
        template_content=template_info["content"],
        template_fields={
            k: MappingField.model_validate(v)
            for k, v in template_info["fields"].items()
        },
    )

    mapping_in_db = (
        db_session.query(MochiMapping)
        .filter(MochiMapping.mochi_deck_id == mochi_deck_id)
        .filter(MochiMapping.user_id == user.id)
        .first()
    )
    if mapping_in_db:
        deck_mapping.lingominer_template_name = mapping_in_db.lingominer_template_name
        deck_mapping.lingominer_template_id = mapping_in_db.lingominer_template_id

        for field_id, field in deck_mapping.template_fields.items():
            if mapping := mapping_in_db.mapping.get(field_id):
                field.lingominer_field_name = mapping["name"]
                field.lingominer_field_id = mapping["id"]
    return deck_mapping


@router.post("")
async def create_mochi_mapping(
    db_session: Annotated[Session, Depends(get_db_session)],
    mapping_create: MochiMappingCreate,
    user: Annotated[User, Depends(get_current_user)],
):
    existing_mochi_mapping = (
        db_session.query(MochiMapping)
        .filter(MochiMapping.mochi_deck_id == mapping_create.mochi_deck_id)
        .filter(MochiMapping.mochi_template_id == mapping_create.mochi_template_id)
        .filter(MochiMapping.user_id == user.id)
        .first()
    )

    if existing_mochi_mapping:
        db_session.delete(existing_mochi_mapping)

    mapping_create = MochiMapping(
        mochi_deck_id=mapping_create.mochi_deck_id,
        mochi_template_id=mapping_create.mochi_template_id,
        lingominer_template_id=mapping_create.lingominer_template_id,
        lingominer_template_name=mapping_create.lingominer_template_name,
        mapping=mapping_create.mapping,
        user_id=user.id,
    )

    db_session.add(mapping_create)
    db_session.commit()


@router.delete("/{mochi_deck_id}")
async def delete_mochi_mapping(
    db_session: Annotated[Session, Depends(get_db_session)],
    mochi_deck_id: str,
    user: Annotated[User, Depends(get_current_user)],
):
    mochi_mapping = (
        db_session.query(MochiMapping)
        .filter(MochiMapping.mochi_deck_id == mochi_deck_id)
        .filter(MochiMapping.user_id == user.id)
        .first()
    )
    db_session.delete(mochi_mapping)


@router.post("/{mochi_deck_id}/cards", response_model=MochiMapping)
async def create_mochi_cards(
    db_session: Annotated[Session, Depends(get_db_session)],
    mochi_deck_id: str,
    lm_card_id: str,
    user: Annotated[User, Depends(get_current_user)],
):
    card = (
        db_session.query(Card)
        .filter(Card.id == lm_card_id)
        .filter(Card.user_id == user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    mochi_mapping = (
        db_session.query(MochiMapping)
        .filter(MochiMapping.mochi_deck_id == mochi_deck_id)
        .filter(MochiMapping.user_id == user.id)
        .first()
    )
    if not mochi_mapping:
        raise HTTPException(status_code=404, detail="Mochi mapping not found")

    if not user.mochi_api_key:
        raise HTTPException(status_code=400, detail="User has no mochi api key")

    # Map fields from LingoMiner card to Mochi card based on the mapping
    mochi_fields = {}
    card_content = card.content

    for mochi_field_id, field_mapping in mochi_mapping.mapping.items():
        lm_field_name = field_mapping.get("name")
        if lm_field_name and lm_field_name in card_content:
            mochi_fields[mochi_field_id] = {
                "id": mochi_field_id,
                "value": card_content[lm_field_name].get("value"),
            }

    # Prepare payload for Mochi API
    payload = {
        "deck-id": mochi_deck_id,
        "template-id": mochi_mapping.mochi_template_id,
        "fields": mochi_fields,
        "content": "",  # Optional content can be added here if needed
    }

    # Create card in Mochi
    response = requests.post(
        f"{base_url}/cards/", json=payload, auth=(user.mochi_api_key, "")
    )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to create card in Mochi: {response.text}",
        )

    return mochi_mapping
