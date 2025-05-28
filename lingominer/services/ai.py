import asyncio

from openai import AsyncClient
from lingominer.config import config

openai_client = AsyncClient(base_url=config.llm_base_url, api_key=config.llm_api_key)

if __name__ == "__main__":
    result = asyncio.run(
        openai_client.images.generate(
            model="gpt-image-1",
            prompt=(
                "draw a flashcard for English word, the word is 'penguin', "
                "background is white, the top of card is most representative object  of the word, "
                "and the bottom of word in Times New Roman"
            ),
            size="256x256",
        )
    )
    print(result)
