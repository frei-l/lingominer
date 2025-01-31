import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import JSON, Field, SQLModel

class CardStatus(str, Enum):
    NEW = "new"
    LEARNING = "learning"
    DELETED = "deleted"


class CardBase(SQLModel):
    paragraph: str = Field(description="the paragraph where the sentence is in")
    pos_start: int = Field(description="start position of the selection in the text")
    pos_end: int = Field(description="end position of the selection in the text")
    url: Optional[str] = Field(description="url of the page")
    content: dict = Field(description="derived content of the card", sa_type=JSON)


class Card(CardBase, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    status: CardStatus = Field(default=CardStatus.NEW)

    template_id: uuid.UUID = Field(
        description="id of the template", foreign_key="template.id"
    )

    created_at: datetime = Field(default=datetime.now(timezone.utc))
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
