import uuid
import os
import tempfile

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from lingominer.base.deps import get_current_user, get_db_session
from lingominer.base.oss import download_file
from lingominer.cards import chroma as vdb
from lingominer.cards import service as db
from lingominer.logger import logger
from lingominer.integration.service import get_by_id as get_mochi_config_by_id
from lingominer.nlp import generate_note
from lingominer.schemas import BrowserSelection, User
from lingominer.schemas.card import Language, Card, CardStatus
from lingominer.global_env import AUDIO_DIR

router = APIRouter()


@router.get("/")
async def get_all_cards(
    lang: Language = Language.English,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> dict:
    logger.info(f"get cards for user: {user}")
    stmt = select(Card).where(
        Card.user_id == user.id, Card.status == CardStatus.NEW, Card.lang == lang
    )
    cards = db_session.exec(stmt).all()
    return {"cards": cards}


@router.post("/")
async def create_a_new_card(
    item: BrowserSelection,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> dict:
    logger.info(f"receive selection request: {item}")
    card_base = await generate_note(item)
    logger.info(f"generate card: {card_base}")
    card = db.create(db_session, card_base, user)
    logger.info(f"save card: {card}")
    # vdb.upsert_card(card)

    return {"card_id": card.id}


@router.get("/search")
async def search_cards(
    query: str,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    result = vdb.search_cards(query)
    logger.info(f"search result: {result}")
    cards = []
    for id, word, score in zip(
        result["ids"][0], result["documents"][0], result["distances"][0]
    ):
        cards.append({"id": id, "word": word, "score": score})
    return cards


@router.delete("/{card_id}")
async def delete_a_card(
    card_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    db.delete(db_session, card_id)
    vdb.delete_card(card_id)
    return {"message": "Card deleted successfully"}


@router.post("/{card_id}/mochi/{config_id}", dependencies=[Depends(get_current_user)])
async def create_a_mochi_card(
    card_id: uuid.UUID,
    config_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
):
    # Fetch the card from the database
    card = db.get_by_id(db_session, card_id)
    card.status = CardStatus.LEARNING
    db_session.commit()
    config = get_mochi_config_by_id(db_session, config_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    if not config:
        raise HTTPException(status_code=404, detail="Mochi config not found")

    # Prepare the Mochi API request payload
    mochi_payload = {
        "content": f"{card.word}: {card.explanation}",
        "deck-id": config.deck_id,
        "template-id": config.template_id,
        "fields": {
            config.fields[str(field.id)]: {
                "id": config.fields[str(field.id)],
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
    card_id = response.json()["id"]

    async with httpx.AsyncClient() as client:
        file_name = card.simple_sentence_audio.removeprefix(
            "![simple_sentence]("
        ).removesuffix(")")
        url = f"https://app.mochi.cards/api/cards/{card_id}/attachments/{file_name}"
        if os.getenv("OSS_ENABLED") == "true":
            with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                download_file("lingominer", file_name, f.name)
                data = {"file": (file_name, f, "audio/wav")}
                attachment_response = await client.post(url, files=data, auth=auth)
        else:
            file_path = AUDIO_DIR / file_name
            with open(file_path, "rb") as audio_file:
                data = {"file": (file_name, audio_file, "audio/wav")}
                attachment_response = await client.post(url, files=data, auth=auth)

    if attachment_response.status_code != 200:
        raise HTTPException(
            status_code=attachment_response.status_code,
            detail=f"{attachment_response.text}",
        )

    return {
        "message": "Mochi card created successfully",
        "mochi_response": response.json(),
    }
