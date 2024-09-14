from sqlmodel import Field, SQLModel


import uuid
from datetime import datetime, timezone


class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    username: str
    hash_token: str
    created_at: datetime = Field(default=datetime.now(timezone.utc))