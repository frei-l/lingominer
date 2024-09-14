from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from enum import Enum
import uuid

if TYPE_CHECKING:
    from lingominer.schemas.integration import MochiConfig



###### Field

class MappingFieldSrc(str, Enum):
    lang = "lang"
    word = "word"
    lemma = "lemma"
    frequency = "frequency"
    explanation = "explanation"
    sentence = "sentence"
    simple_sentence = "simple_sentence"
    expression = "expression"
    selection = "selection"
    paragraph = "paragraph"
    summary = "summary"
    url = "url"


class MappingFieldType(str, Enum):
    text = "text"
    audio = "audio"
    image = "image"


class MappingFieldBase(SQLModel):
    foreign_id: str
    name: str
    type: MappingFieldType
    source: Optional[MappingFieldSrc] = None

class MappingFieldCreate(MappingFieldBase):
    pass


class MappingField(MappingFieldBase, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    mapping_id: uuid.UUID = Field(foreign_key="mapping.id")
    mapping: "Mapping" = Relationship(back_populates="fields")

###### Mapping

class MappingBase(SQLModel):
    lang: str
    name: str


class MappingCreate(MappingBase):
    fields: list[MappingFieldCreate]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "lang": "en",
                    "name": "My Mapping",
                    "fields": [
                        {"foreign_id": "word", "name": "Word", "type": "text", "source": "word"},
                        {"foreign_id": "frequency", "name": "Frequency", "type": "text", "source": "frequency"},
                    ]
                }
            ]
        } 
    }


class Mapping(MappingBase, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    user_id: uuid.UUID
    created_at: datetime = Field(default=datetime.now(timezone.utc))

    fields: list[MappingField] = Relationship(back_populates="mapping")

    mochi_config: list["MochiConfig"] = Relationship(back_populates="mapping")
