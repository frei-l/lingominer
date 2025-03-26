from openai import AsyncClient

from lingominer.config import config

openai_client = AsyncClient(
    base_url=config.llm_base_url,
    api_key=config.llm_api_key
)

