import asyncio
import json
from typing import Any, Callable, Literal, Optional

from jinja2 import Template
from openai import AsyncClient
from pydantic import BaseModel

from lingominer.config import config
from lingominer.logger import logger

openai_client = AsyncClient(
    base_url=config.llm_base_url,
    api_key=config.llm_api_key,
)


class FieldDefinition(BaseModel):
    name: str
    type: Literal["text", "audio"]
    description: str


class Task(BaseModel):
    name: str
    action: str
    inputs: list[str]
    outputs: list[FieldDefinition]

    # Completion Task
    prompt: Optional[str] = None


class State:
    def __init__(self, value: Any = None):
        self.semaphore = asyncio.Semaphore(0)
        if value is not None:
            self.value = value
            self.semaphore.release()
        else:
            self.value = None

    def set(self, value):
        self.value = value
        self.semaphore.release()

    async def get(self):
        async with self.semaphore:
            return self.value


class Context:
    def __init__(self, context: dict = {}):
        self.context: dict[str, State] = {}
        self.init_keys = set(context.keys())
        for key, value in context.items():
            self.context[key] = State(value)

    def add(self, key: str, value: Any = None):
        self.context[key] = State(value)

    async def get(self, key: str) -> Any:
        if key not in self.context:
            raise ValueError(f"Key {key} not found in context")
        value = await self.context[key].get()
        return value

    def set(self, key: str, value):
        if key not in self.context:
            raise ValueError(f"Key {key} not found in context")
        self.context[key].set(value)

    def keys(self):
        return self.context.keys()

    def dump(self, exclude_init: bool = True):
        if exclude_init:
            return {
                key: state.value
                for key, state in self.context.items()
                if key not in self.init_keys
            }
        return {key: state.value for key, state in self.context.items()}

    def __str__(self):
        return str({key: state.value for key, state in self.context.items()})


class Flow:
    def __init__(self, context: Context = Context()):
        self.context = context
        self.actions: dict[str, Callable] = {}
        self.tasks: list[Task] = []
        # default actions
        self.add_action("completion", completion)

    def add_action(self, name: str, func: Callable):
        self.actions[name] = func

    def add_task(self, task: Task):
        for output in task.outputs:
            if output.name not in self.context.keys():
                self.context.add(output.name)
        self.tasks.append(task)

    async def _execute_task(self, task: Task):
        inputs = {}
        for input in task.inputs:
            inputs[input] = await self.context.get(input)
        outputs = await self.actions[task.action](self.context, task, inputs)
        for output in task.outputs:
            self.context.set(output.name, outputs[output.name])

    async def run(self, timeout: int = 30):
        async with asyncio.timeout(timeout):
            async with asyncio.TaskGroup() as tg:
                for task in self.tasks:
                    tg.create_task(self._execute_task(task))
        return self.context


def render_prompt(prompt: str, inputs: dict, outputs: list[FieldDefinition]) -> str:
    # Instruction
    template = Template(prompt)
    prompt_rendered = template.render(**inputs)
    # Output Format
    fields_description = "\n".join(
        [f"- `{field.name}`: {field.description}" for field in outputs]
    )
    output_format = (
        "Your task is to generate a JSON object that adheres "
        "to the following schema:\n\n"
        "The schema is defined as follows:\n"
        f"{fields_description}\n\n"
        "Please ensure the output JSON strictly follows this schema. Do not include extra fields."
    )
    # Final Prompt
    final_prompt = (
        "# Instruction\n"
        f"{prompt_rendered}\n\n"
        "# Output Format\n"
        f"{output_format}\n\n"
        "# Output"
    )
    logger.debug(f"Final Prompt: {final_prompt}")
    return final_prompt


async def completion(context: Context, task: Task, inputs: dict) -> dict:
    for init_key in context.init_keys:
        inputs[init_key] = await context.get(init_key)
    response = await openai_client.chat.completions.create(
        model=config.llm_base_model,
        messages=[
            {
                "role": "system",
                "content": render_prompt(task.prompt, inputs, task.outputs),
            },
        ],
        response_format={"type": "json_object"},
    )
    dict_result = json.loads(response.choices[0].message.content)
    logger.debug(f"Completion Result: {response.choices[0].message.content}")
    return dict_result


# async def lookup(inputs: dict) -> str:
#     if len(inputs) > 1:
#         raise ValueError("Lookup only support one input")
#     query = list(inputs.values())[0]
#     pass

# async def toSpeech(inputs: dict) -> str:
#     if len(inputs) > 1:
#         raise ValueError("toSpeech only support one input")
#     text = list(inputs.values())[0]
#     pass

# async def scrapeUrl(inputs: dict) -> str:
#     if len(inputs) > 1:
#         raise ValueError("scrapeUrl only support one input")
#     url = list(inputs.values())[0]
#     pass
