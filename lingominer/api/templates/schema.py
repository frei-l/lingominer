import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel


## Template Field


class FieldType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"


class TemplateFieldCreate(BaseModel):
    name: str
    type: FieldType
    description: Optional[str] = None
    generation_id: Optional[uuid.UUID] = None


class TemplateFieldUpdate(BaseModel):
    description: Optional[str] = None
    type: Optional[FieldType] = None


class TemplateFieldResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: FieldType
    description: Optional[str] = None
    source_id: uuid.UUID


## Generation


class GenerationCreate(BaseModel):
    name: str
    method: str
    prompt: Optional[str] = None
    inputs: list[str]


class GenerationUpdate(BaseModel):
    name: Optional[str] = None
    method: Optional[str] = None
    prompt: Optional[str] = None
    inputs: Optional[list[str]] = None


class GenerationResponse(BaseModel):
    id: uuid.UUID
    name: str
    method: str
    prompt: Optional[str] = None


class GenerationDetailResponse(GenerationResponse):
    template_id: uuid.UUID
    inputs: list[TemplateFieldResponse]
    outputs: list[TemplateFieldResponse]


## Template


class TemplateCreate(BaseModel):
    name: str
    lang: str


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    lang: str


class TemplateDetailResponse(TemplateResponse):
    fields: list[TemplateFieldResponse]
    generations: list[GenerationResponse]
