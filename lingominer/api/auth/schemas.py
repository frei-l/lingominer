from typing import Optional
from datetime import datetime

from sqlmodel import Field, SQLModel


class UserDetail(SQLModel):
    id: str
    name: str
    api_keys: list["ApiKeyDetail"]
    mochi_api_key: Optional[str]

    created_at: datetime
    modified_at: datetime


class ApiKeyDetail(SQLModel):
    id: str
    key: str

    created_at: datetime
    modified_at: datetime


class SettingsUpdate(SQLModel):
    mochi_api_key: Optional[str] = Field(description="mochi api key")
