from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from lingominer.api.auth.security import get_current_user
from lingominer.api.cards.schema import CardCreate
from lingominer.api.templates.service import get_template
from lingominer.ctx import user_id
from lingominer.database import get_db_session
from lingominer.flow.algo import Context, FieldDefinition, Flow, Task
from lingominer.models.card import Card

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[Card])
async def get_cards(
    db_session: Annotated[Session, Depends(get_db_session)],
    template_id: Optional[str] = None,
):
    if template_id:
        stmt = select(Card).where(Card.template_id == template_id)
    else:
        stmt = select(Card)
    cards = db_session.exec(stmt).all()
    return cards


@router.post("", response_model=Card)
async def create_card_view(
    db_session: Annotated[Session, Depends(get_db_session)],
    card_create: CardCreate,
    template_id: str,
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

    card_from_template = Card(
        template_id=template_id,
        user_id=user_id.get(),
        **card_create.model_dump(),
        content=result.dump(),
    )
    db_session.add(card_from_template)
    db_session.commit()
    db_session.refresh(card_from_template)
    return card_from_template
