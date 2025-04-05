from sqlmodel import Field, Relationship, SQLModel
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

    notes: list["Note"] = Relationship(back_populates="passage")

    created_at: datetime = Field(default=datetime.now(timezone.utc))
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class Note(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        default_factory=lambda: "note_" + uuid.uuid4().hex,
    )
    user_id: str = Field(description="user id", foreign_key="user.id")

    passage_id: str = Field(foreign_key="passage.id")
    passage: "Passage" = Relationship(back_populates="notes")

    content: str = Field(description="content of the note")
    selected_text: str = Field(description="selected text")
    context: str = Field(description="context of the selected text")
    paragraph_index: int = Field(description="paragraph index of the selected text")
    start_index: int = Field(description="start index of the selected text")
    end_index: int = Field(description="end index of the selected text")

    created_at: datetime = Field(default=datetime.now(timezone.utc))
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
