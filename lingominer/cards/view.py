import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from lingominer.cards import service as db
from lingominer.core.deps import get_current_user, get_db_session
from lingominer.logger import logger
from lingominer.mochi.service import (
    get_by_id as get_mochi_config_by_id,
)
from lingominer.nlp import load
from lingominer.schemas.card import CardBase
from lingominer.schemas.source import BrowserSelection
from lingominer.schemas.user import User

router = APIRouter()


@router.get("/")
async def get_all_cards(
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> dict:
    logger.info(f"get cards for user: {user}")
    cards = db.get(db_session, user)
    return {"cards": cards}


@router.post("/")
async def create_a_new_card(
    item: BrowserSelection,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> dict:
    logger.info(f"receive selection request: {item}")
    nlp = load(item.lang)
    card: CardBase = nlp.generate(item)
    logger.info(f"generate card: {card}")
    card_id = db.create(db_session, card, user)
    logger.info(f"save card: {card_id}")

    return {"card_id": card_id}


@router.delete("/{card_id}")
async def delete_a_card(
    card_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    pass


@router.post("/{card_id}/mochi/{config_id}", dependencies=[Depends(get_current_user)])
async def create_a_mochi_card(
    card_id: uuid.UUID,
    config_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
):
    # Fetch the card from the database
    card = db.get_by_id(db_session, card_id)
    config = get_mochi_config_by_id(db_session, config_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    if not config:
        raise HTTPException(status_code=404, detail="Mapping not found")

    # Prepare the Mochi API request payload
    mochi_payload = {
        "content": f"{card.word}: {card.explanation}",
        "deck-id": config.deck_id,
        "template-id": config.template_id,
        "fields": {
            field.foreign_id: {
                "id": field.foreign_id,
                "value": getattr(card, field.source),
            }
            for field in config.mapping.fields
        },
    }
    auth = httpx.BasicAuth(username=config.api_key, password="")
    # Make the request to the Mochi API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://app.mochi.cards/api/cards/",
            json=mochi_payload,
            headers={
                "Content-Type": "application/json",
            },
            auth=auth,
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail=f"{response.json()}"
        )

    return {
        "message": "Mochi card created successfully",
        "mochi_response": response.json(),
    }
