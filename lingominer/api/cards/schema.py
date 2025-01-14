from pydantic import BaseModel
from typing import Optional

class CardCreate(BaseModel):
    paragraph: str
    pos_start: int
    pos_end: int
    url: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "paragraph": """\nEllen van Langen rollte das Feld von hinten auf, als sie 1992 olympisches Gold über 800 Meter gewann. Es \
war eine von zwei Goldmedaillen der niederländischen Delegation. Insgesamt holte das Team Oranje in Barce\
lona 15 Mal Edelmetall. Das reichte für Platz 20 im Medaillenspiegel.""",
                    "pos_start": 239,
                    "pos_end": 246,
                    "url": 'https://www.tagesschau.de/ausland/europa/olympische-spiele-niederlande-100.html',
                    "lang": 'de'
                }
            ]
        }
    }

class CardUpdate(BaseModel):
    content: dict
