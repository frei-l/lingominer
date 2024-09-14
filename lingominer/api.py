import os.path
import uuid
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx

from lingominer.database import (
    create_user,
    get_cards,
    get_mappings,
    save_card,
    save_mapping,
    verify_user,
    get_card_by_id,
    create_mochi_config,
    get_mochi_config_by_id,
    get_mochi_configs,
)
from lingominer.logger import logger
from lingominer.nlp import load
from lingominer.schemas.card import CardBase
from lingominer.schemas.mapping import MappingCreate
from lingominer.schemas.source import BrowserSelection
from lingominer.schemas.integration import MochiConfigCreate
from lingominer.schemas.user import User
from lingominer.schemas import engine
from sqlmodel import Session

app = FastAPI(title="api")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "card.db")
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_scheme = HTTPBearer()


def get_db_session():
    with Session(engine, autoflush=False) as session:
        yield session


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db_session: Session = Depends(get_db_session),
):
    user = verify_user(db_session, credentials.credentials)
    if user:
        return user
    raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/cards")
async def app_get_cards(
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> dict:
    logger.info(f"get cards for user: {user}")
    cards = get_cards(db_session, user)
    return {"cards": cards}


@app.post("/cards/")
async def add_card(
    item: BrowserSelection,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> dict:
    logger.info(f"receive selection request: {item}")
    nlp = load(item.lang)
    card: CardBase = nlp.generate(item)
    logger.info(f"generate card: {card}")
    card_id = save_card(db_session, card, user)
    logger.info(f"save card: {card_id}")
    return {"card_id": card_id}


@app.delete("/cards/{card_id}")
async def delete_card(
    card_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    pass


@app.post(
    "/cards/{card_id}/mochi/{config_id}", dependencies=[Depends(get_current_user)]
)
async def mochi_card(
    card_id: uuid.UUID,
    config_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
):
    # Fetch the card from the database
    card = get_card_by_id(db_session, card_id)
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


@app.get("/mappings/")
async def get_mappings_view(
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    mappings = get_mappings(db_session, user)
    return {"mappings": mappings}


@app.post("/mappings/", status_code=status.HTTP_201_CREATED)
async def add_mappings(
    data: MappingCreate,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    mapping_id = save_mapping(db_session, data, user)
    return {"mapping_id": mapping_id}


@app.post("/users/")
async def add_user(username: str, db_session: Session = Depends(get_db_session)):
    token = create_user(db_session, username)
    return {"token": token}


@app.get("/users/me")
async def get_user(user: User = Depends(get_current_user)):
    return {"username": user.username}


@app.post(
    "/mochi/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def add_mochi_config(
    config: MochiConfigCreate,
    db_session: Session = Depends(get_db_session),
):
    config_id = create_mochi_config(db_session, config)
    return {"config_id": config_id}


@app.get("/mochi/", dependencies=[Depends(get_current_user)])
async def get_mochi_configs_views(
    db_session: Session = Depends(get_db_session),
):
    configs = get_mochi_configs(db_session)
    return {"configs": configs}


@app.get("/mochi/{config_id}", dependencies=[Depends(get_current_user)])
async def get_mochi_config(
    config_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
):
    config = get_mochi_config_by_id(db_session, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Mochi config not found")
    return config
