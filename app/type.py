from pydantic import BaseModel
from typing import Dict
from enum import IntEnum, Enum


class FieldMapping(BaseModel):
    name: str
    type: str
    src: str | None = None


class BaseMapping(BaseModel):
    user_id: int
    lang: str
    template_name: str
    template_id: str
    fields: Dict[str, FieldMapping]


class CardType(IntEnum):
    singleWord = 1
    expression = 2


class Language(str, Enum):
    English = "en"
    German = "de"
    Japanese = "jp"


class BrowserSelection(BaseModel):
    start: int
    end: int
    text: str
    lang: str
    url: str | None = None


class BaseCard(BaseModel):
    type: CardType
    lang: Language
    selection: str
    word: str
    lemma: str
    frequency: int
    sentence: str
    expression: str
    pos_start: int
    pos_end: int
    paragraph: str
    summary: str
    url: str
