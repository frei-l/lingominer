from sqlmodel import Field, SQLModel
import uuid
from datetime import datetime, timezone


class Passage(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        default_factory=lambda: "passage_" + uuid.uuid4().hex,
    )
    user_id: str = Field(description="user id", foreign_key="user.id")
    title: str = Field(description="title of the passage")
    url: str = Field(description="url of the passage")
    content: str = Field(description="content of the passage")

    created_at: datetime = Field(default=datetime.now(timezone.utc))
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
