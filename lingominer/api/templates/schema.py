from typing import Optional
from pydantic import BaseModel, model_validator
from enum import Enum


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


class GenerationCreate(BaseModel):
    method: str
    prompt: Optional[str] = None
    inputs: list[str]
    outputs: list[TemplateFieldCreate]

    @model_validator(mode="after")
    def validate_prompt(self):
        if self.method == "completion" and self.prompt is None:
            raise ValueError("Prompt is required for completion method")
        return self
