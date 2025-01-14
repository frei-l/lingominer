import uuid

from fastapi import APIRouter
from sqlmodel import Session

from lingominer.api.cards import service as db
from lingominer.api.cards.schema import CardCreate
from lingominer.api.templates.service import get_template
from lingominer.flow.algo import Context, Flow, Task
from lingominer.models.card import Card

router = APIRouter()


@router.get("/cards", response_model=list[Card])
async def get_cards(db_session: Session, template_id: uuid.UUID):
    cards = db.get(db_session, template_id)
    return cards


@router.post("/cards")
async def create_card(
    db_session: Session, card_create: CardCreate, template_id: uuid.UUID
):
    template = get_template(db_session, template_id)
    setup_context = Context(card_create.model_dump())
    flow = Flow(setup_context)
    for generation in template.generations:
        flow.add_task(
            Task(
                name=generation.name,
                action=generation.method,
                inputs=generation.inputs,
                outputs=generation.outputs,
                prompt=generation.prompt,
            )
        )
    result = await flow.run()
    card = db.create(
        db_session, card_create=card_create, template_id=template_id, content=result
    )
    return card
