from sqlmodel import SQLModel, Field, Relationship, JSON
import uuid

from lingominer.schemas.mapping import Mapping

class MochiConfigCreate(SQLModel):
    lang: str
    deck_id: str
    template_id: str
    template_name: str
    fields: dict[str, dict[str, str]]

class MochiConfig(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    user_id: uuid.UUID = Field(foreign_key="user.id")

    api_key: str
    deck_id: str
    template_id: str
    template_name: str

    fields: dict[uuid.UUID, str] = Field(sa_type=JSON)
    """the key is the field id in lingominer, the value is id in mochi"""

    mapping_id: uuid.UUID = Field(foreign_key="mapping.id")
    mapping: "Mapping" = Relationship()