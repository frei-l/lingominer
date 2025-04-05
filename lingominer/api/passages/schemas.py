from datetime import datetime

from sqlmodel import Field, SQLModel


class PassageList(SQLModel):
    id: str = Field(description="id of the passage")
    user_id: str = Field(description="user id")

    title: str = Field(description="title of the passage")
    url: str = Field(description="url of the passage")

    created_at: datetime
    modified_at: datetime


class PassageDetail(PassageList):
    content: str = Field(description="content of the passage")
    notes: list["NoteDetail"]


class NoteCreate(SQLModel):
    selected_text: str
    context: str
    paragraph_index: int
    start_index: int
    end_index: int


class NoteDetail(SQLModel):
    id: str = Field(description="id of the note")
    content: str = Field(description="content of the note")
    selected_text: str = Field(description="selected text")
    context: str = Field(description="context of the selected text")
    paragraph_index: int = Field(description="paragraph index of the selected text")
    start_index: int = Field(description="start index of the selected text")
    end_index: int = Field(description="end index of the selected text")

    created_at: datetime
    modified_at: datetime
