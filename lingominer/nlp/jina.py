import os

import requests
from functools import lru_cache

READER_BASE_URL = "https://r.jina.ai/"


@lru_cache(maxsize=32)
def scrape_url(url: str):
    headers = {
        "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
        "X-Return-Format": "text",
    }
    reader_response = requests.get(READER_BASE_URL + url, headers=headers)
    return reader_response.text
