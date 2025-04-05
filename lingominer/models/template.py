import uuid
from enum import StrEnum
from typing import Optional

from sqlmodel import Column, Enum, Field, Relationship, SQLModel, UniqueConstraint


class FieldType(StrEnum):
    TEXT = "text"
    AUDIO = "audio"


class TemplateLang(StrEnum):
    en = "en"
    de = "de"
    jp = "jp"


class Template(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        default_factory=lambda: "template_" + uuid.uuid4().hex,
    )
    user_id: str = Field(description="user id", foreign_key="user.id")
    name: str = Field(description="name of the template")
    lang: TemplateLang = Field(
        description="language of the template",
        sa_column=Column(Enum(TemplateLang)),
    )

    generations: list["Generation"] = Relationship(back_populates="template")
    fields: list["TemplateField"] = Relationship(back_populates="template")


class GenerationInputFieldLink(SQLModel, table=True):
    generation_id: Optional[str] = Field(
        default=None, foreign_key="generation.id", primary_key=True
    )
    field_id: Optional[str] = Field(
        default=None, foreign_key="templatefield.id", primary_key=True
    )


class Generation(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        default_factory=lambda: "generation_" + uuid.uuid4().hex,
    )
    user_id: str = Field(description="user id", foreign_key="user.id")
    name: str = Field(description="name of the generation")

    template_id: str = Field(foreign_key="template.id")
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
    id: str = Field(
        primary_key=True,
        default_factory=lambda: "field_" + uuid.uuid4().hex,
    )
    user_id: str = Field(description="user id", foreign_key="user.id")
    name: str = Field(description="name of the field")
    type: FieldType = Field(default=FieldType.TEXT)
    description: str = Field(default="")

    template_id: str = Field(foreign_key="template.id")
    template: "Template" = Relationship(back_populates="fields")

    source_id: Optional[str] = Field(default=None, foreign_key="generation.id")
    source: Optional[Generation] = Relationship(
        back_populates="outputs",
    )

    referenced: list[Generation] = Relationship(
        back_populates="inputs",
        link_model=GenerationInputFieldLink,
    )
