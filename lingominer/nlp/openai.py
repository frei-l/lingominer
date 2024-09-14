from langfuse.openai import OpenAI
from langfuse.model import ChatPromptClient
from langfuse.decorators import langfuse_context, observe

import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_PROXY"),
)


@observe(as_type="generation")
def llm_call(prompt: ChatPromptClient, **kwargs):
    message = prompt.compile(**kwargs)
    langfuse_context.update_current_observation(
        name=prompt.name,
        prompt=prompt
        )
    response = client.chat.completions.create(
        model=prompt.config["model"],
        messages=[{"role": "system", "content": message}],
    )
    return response.choices[0].message.content
