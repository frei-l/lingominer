from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
import uuid
from typing import Optional


class FieldType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"



class TemplateLang(str, Enum):
    EN = "en"
    DE = "de"
    JP = "jp"


class Template(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str = Field(description="name of the template")
    lang: str = Field(description="language of the template")

    generations: list["Generation"] = Relationship(back_populates="template")
    fields: list["TemplateField"] = Relationship(back_populates="template")


class GenerationInputFieldLink(SQLModel, table=True):
    generation_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="generation.id", primary_key=True
    )
    field_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="templatefield.id", primary_key=True
    )


class Generation(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str = Field(description="name of the generation")

    template_id: uuid.UUID = Field(foreign_key="template.id")
    template: "Template" = Relationship(back_populates="generations")

    method: str = Field(default="completion")

    prompt: str = Field(default="")

    inputs: list["TemplateField"] = Relationship(
        back_populates="referenced",
        link_model=GenerationInputFieldLink,
    )
    outputs: list["TemplateField"] = Relationship(
        back_populates="source",
    )


class TemplateField(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "template_id", name="unique_field_name"),
    )
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str = Field(description="name of the field")
    type: FieldType = Field(default=FieldType.TEXT)
    description: str = Field(default="")

    template_id: uuid.UUID = Field(foreign_key="template.id")
    template: "Template" = Relationship(back_populates="fields")

    source_id: Optional[uuid.UUID] = Field(default=None, foreign_key="generation.id")
    source: Optional[Generation] = Relationship(
        back_populates="outputs",
    )

    referenced: list[Generation] = Relationship(
        back_populates="inputs",
        link_model=GenerationInputFieldLink,
    )
