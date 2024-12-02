from langfuse.openai import openai
from langfuse.model import ChatPromptClient
from lingominer.nlp.langfuse import observe, langfuse_context
import json
import os

client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_PROXY"),
)


@observe(name="LLM call")
async def llm_call(prompt: ChatPromptClient, **kwargs):
    message = prompt.compile(**kwargs)
    config = prompt.config
    if config.get("model") == "gpt-4o":
        config["model"] = os.getenv("LINGOMINER_MODEL_1")
    elif config.get("model") == "gpt-4o-mini":
        config["model"] = os.getenv("LINGOMINER_MODEL_2")

    response = await client.chat.completions.create(
        messages=[{"role": "system", "content": message}],
        langfuse_prompt=prompt,
        name=prompt.name,
        **config,
    )
    langfuse_context.update_current_observation(
        input=kwargs,
        output=response.choices[0].message.content,
    )
    if config.get("response_format"):
        return json.loads(response.choices[0].message.content)
    else:
        return response.choices[0].message.content
