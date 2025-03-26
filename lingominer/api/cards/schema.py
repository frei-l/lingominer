from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from lingominer.models.card import CardStatus


class CardCreate(BaseModel):
    paragraph: str
    pos_start: int
    pos_end: int
    url: Optional[str] = None

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
    created_at: datetime
    modified_at: datetime
