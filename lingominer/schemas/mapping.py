from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum
import uuid


###### Field


class MappingFieldSrc(str, Enum):
    lang = "lang"
    word = "word"
    lemma = "lemma"
    frequency = "frequency"
    explanation = "explanation"
    sentence = "sentence"
    simple_sentence = "simple_sentence"
    simple_sentence_audio = "simple_sentence_audio"
    expression = "expression"
    selection = "selection"
    paragraph = "paragraph"
    summary = "summary"
    url = "url"


class MappingFieldBase(SQLModel):
    name: str
    source: MappingFieldSrc


class MappingField(MappingFieldBase, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    mapping_id: uuid.UUID = Field(foreign_key="mapping.id")
    mapping: "Mapping" = Relationship(back_populates="fields")


###### Mapping


class MappingBase(SQLModel):
    lang: str
    name: str


class Mapping(MappingBase, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    user_id: uuid.UUID = Field(foreign_key="user.id")

    fields: list[MappingField] = Relationship(back_populates="mapping")

    created_at: datetime = Field(default=datetime.now(timezone.utc))
