from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from lingominer.models.card import CardStatus


class CardCreate(BaseModel):
    paragraph: str
    pos_start: int
    pos_end: int

    template_id: Optional[str] = Field(
        default=None,
        description="id of template intended to be used, if not provided, "
        "the language will be detected and a template will be used accordingly",
    )
    url: Optional[str] = Field(
        default=None,
        description="url of the page where the sentence is from, if not provided, ",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "paragraph": "In addition to its rings, Saturn has 25 satellites that measure at least 6 miles (10 kilometers) in diameter, and several smaller satellites. The largest of Saturn’s satellites, Titan, has a diameter of about 3,200 miles—larger than the planets Mercury and Pluto. Titan is one of the few satellites in the solar system known to have an atmosphere. Its atmosphere consists largely of nitrogen. Many of Saturn’s satellites have large craters For example, Mimas has a crater that covers about one-third the diameter of the satellite.",
                    "pos_start": 432,
                    "pos_end": 439,
                }
            ]
        }
    }


class CardResponse(BaseModel):
    id: str
    paragraph: str
    pos_start: int
    pos_end: int
    url: Optional[str] = None
    content: dict
    status: CardStatus
    template_id: str
    created_at: datetime
    modified_at: datetime
