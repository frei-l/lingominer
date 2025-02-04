import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from lingominer.api.cards import service as db
from lingominer.api.cards.schema import CardCreate
from lingominer.api.templates.service import get_template
from lingominer.flow.algo import Context, Flow, Task, FieldDefinition
from lingominer.database import get_db_session
from lingominer.models.card import Card

router = APIRouter()


@router.get("", response_model=list[Card])
async def get_cards(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: Optional[uuid.UUID] = None,
):
    cards = db.get(db_session, template_id)
    return cards


@router.post("", response_model=Card)
async def create_card_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    card_create: CardCreate,
    template_id: uuid.UUID,
):
    template = get_template(db_session, template_id)
    setup_context = Context(
        {
            "paragraph": card_create.paragraph,
            "decorated_paragraph": (
                card_create.paragraph[: card_create.pos_start]
                + "@@"
                + card_create.paragraph[card_create.pos_start : card_create.pos_end]
                + "@@"
                + card_create.paragraph[card_create.pos_end :]
            ),
        }
    )
    flow = Flow(setup_context)
    for generation in template.generations:
        flow.add_task(
            Task(
                name=generation.name,
                action=generation.method,
                inputs=[f.name for f in generation.inputs],
                outputs=[
                    FieldDefinition(
                        name=f.name,
                        type=f.type,
                        description=f.description,
                    )
                    for f in generation.outputs
                ],
                prompt=generation.prompt,
            )
        )
    result = await flow.run()
    card = db.create(
        db_session,
        card_create=card_create,
        template_id=template_id,
        content=result.dump(exclude_init=True),
    )
    return card
