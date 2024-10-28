from langfuse.openai import OpenAI
from langfuse.model import ChatPromptClient
import json
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_PROXY"),
)


def llm_call(prompt: ChatPromptClient, **kwargs):
    message = prompt.compile(**kwargs)
    config = prompt.config
    if config.get("model") == "gpt-4o":
        config["model"] = os.getenv("LINGOMINER_MODEL_1")
    elif config.get("model") == "gpt-4o-mini":
        config["model"] = os.getenv("LINGOMINER_MODEL_2")

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": message}],
        langfuse_prompt=prompt,
        name=prompt.name,
        **config
    )
    if config.get("response_format"):
        return json.loads(response.choices[0].message.content)
    else:
        return response.choices[0].message.content
