from typing import TypedDict

from sqlmodel import Field, JSON, SQLModel


class MochiMappingField(TypedDict):
    id: str
    name: str


class MochiMapping(SQLModel, table=True):
    mochi_deck_id: str = Field(primary_key=True)
    mochi_template_id: str

    user_id: str

    lingominer_template_id: str
    lingominer_template_name: str
    mapping: dict[str, MochiMappingField] = Field(
        description="mapping of the mochi template to the lingominer template",
        sa_type=JSON,
    )
