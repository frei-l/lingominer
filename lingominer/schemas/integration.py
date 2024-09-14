from sqlmodel import SQLModel, Field, Relationship
import uuid
from typing import TYPE_CHECKING
# https://github.com/fastapi/sqlmodel/discussions/942
if TYPE_CHECKING:
    from lingominer.schemas.mapping import Mapping

class MochiConfigBase(SQLModel):
    api_key: str
    deck_id: str
    template_id: str
    mapping_id: uuid.UUID = Field(foreign_key="mapping.id")

class MochiConfig(MochiConfigBase, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    mapping: "Mapping" = Relationship(back_populates="mochi_config")

class MochiConfigCreate(MochiConfigBase):
    pass