import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, model_validator


class FieldType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"


class TemplateCreate(BaseModel):
    name: str
    lang: str


class TemplateFieldCreate(BaseModel):
    name: str
    type: FieldType
    description: Optional[str] = None


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    lang: str


class TemplateDetailResponse(TemplateResponse):
    fields: list["TemplateFieldResponse"]
    generations: list["GenerationResponse"]


class TemplateFieldResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: FieldType
    description: Optional[str] = None
    source_id: uuid.UUID


class GenerationCreate(BaseModel):
    name: str
    method: str
    prompt: Optional[str] = None
    inputs: list[str]
    outputs: list[TemplateFieldCreate]

    @model_validator(mode="after")
    def validate_prompt(self):
        if self.method == "completion" and self.prompt is None:
            raise ValueError("Prompt is required for completion method")
        return self


class GenerationResponse(BaseModel):
    id: uuid.UUID
    name: str
    method: str
    prompt: Optional[str] = None


class GenerationDetailResponse(GenerationResponse):
    template_id: uuid.UUID
    inputs: list[TemplateFieldResponse]
    outputs: list[TemplateFieldResponse]
