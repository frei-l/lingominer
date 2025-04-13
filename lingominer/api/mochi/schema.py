from sqlmodel import SQLModel

from lingominer.models.mochi import MochiMappingField


class MochiMappingCreate(SQLModel):
    lingominer_template_id: str
    lingominer_template_name: str
    mapping: dict[str, MochiMappingField]
