import requests

from lingominer.config import config


def scrape_url(url: str):
    url = f"https://r.jina.ai/{url}"
    headers = {"Authorization": f"Bearer {config.jina_api_key}"}

    response = requests.get(url, headers=headers)
    return response.text
