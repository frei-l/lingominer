from pydantic import BaseModel


class BrowserSelection(BaseModel):
    start: int
    end: int
    text: str
    lang: str
    url: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "start": 239,
                    "end": 246,
                    "text": """\nEllen van Langen rollte das Feld von hinten auf, als sie 1992 olympisches Gold über 800 Meter gewann. Es \
war eine von zwei Goldmedaillen der niederländischen Delegation. Insgesamt holte das Team Oranje in Barce\
lona 15 Mal Edelmetall. Das reichte für Platz 20 im Medaillenspiegel.""",
                    "lang": 'de',
                    "url": 'https://www.tagesschau.de/ausland/europa/olympische-spiele-niederlande-100.html'
                }
            ]
        }
    }
