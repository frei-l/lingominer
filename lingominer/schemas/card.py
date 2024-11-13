from enum import Enum
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid


class CardType(Enum):
    singleWord = 1
    expression = 2


class Language(str, Enum):
    English = "en"
    German = "de"
    Japanese = "jp"


class CardStatus(str, Enum):
    NEW = "new"
    LEARNING = "learning"
    DELETED = "deleted"


class CardBase(SQLModel):
    type: CardType = Field(
        default=CardType.singleWord,
        description="type of the card, single word or expression",
    )
    lang: Language = Field(
        default=Language.English, description="language of the selection"
    )
    selection: str = Field(description="exact what user selected")
    word: str = Field(
        description="most important word in the selection with original form"
    )
    lemma: str = Field(description="the lemma of word")
    frequency: int = Field(description="frequency of the lemma")
    explanation: str = Field(description="explanation of the word in dictionary")
    sentence: str = Field(description="the sentence where the word is in")
    simple_sentence: str = Field(description="the sentence after simplified")
    simple_sentence_audio: str = Field(
        description="file path of the audio of the simplified sentence"
    )
    expression: str = Field(description="the expression when multiple words dectected")
    pos_start: int = Field(description="start position of the selection in the text")
    pos_end: int = Field(description="end position of the selection in the text")
    paragraph: str = Field(description="the paragraph where the sentence is in")
    summary: str = Field(description="summary of the page")
    url: str = Field(description="url of the page")


class Card(CardBase, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    user_id: uuid.UUID
    status: CardStatus = Field(default=CardStatus.NEW)
    created_at: datetime = Field(default=datetime.now(timezone.utc))
