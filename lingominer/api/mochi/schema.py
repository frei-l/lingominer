from pydantic import BaseModel

from lingominer.models.mochi import MochiMappingField


class MochiMappingCreate(BaseModel):
    mochi_deck_id: str
    mochi_template_id: str

    lingominer_template_id: str
    lingominer_template_name: str
    mapping: dict[str, MochiMappingField]


class MochiDeckMappingItem(BaseModel):
    id: str
    name: str

    template_id: str

    lingominer_template_id: str | None = None
    lingominer_template_name: str | None = None


class MappingField(BaseModel):
    id: str
    name: str
    type: str | None = None
    options: dict[str, str | bool] | None = None
    source: str | None = None

    lingominer_field_name: str | None = None
    lingominer_field_id: str | None = None


class MochiDeckMapping(MochiDeckMappingItem):
    template_name: str
    template_content: str
    template_fields: dict[str, MappingField]
