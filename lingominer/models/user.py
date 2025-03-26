import uuid
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        default_factory=lambda: "user_" + uuid.uuid4().hex,
    )
    name: str = Field(description="name of the user")
    api_keys: list["ApiKey"] = Relationship(back_populates="user")

    created_at: datetime = Field(default=datetime.now(timezone.utc))
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class ApiKey(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        default_factory=lambda: "api_key_" + uuid.uuid4().hex,
    )
    key: str = Field(description="api key", unique=True)

    user_id: str = Field(description="user id", foreign_key="user.id")
    user: User = Relationship(back_populates="api_keys")

    created_at: datetime = Field(default=datetime.now(timezone.utc))
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
