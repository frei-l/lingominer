import asyncio
import json
import os
import tempfile
import uuid
from typing import Callable, Literal, Optional, TypedDict
import base64

from jinja2 import Template
from openai import AsyncClient
from pydantic import BaseModel

from lingominer.config import config
from lingominer.logger import logger
from lingominer.services.azure_speech import generate_audio
from lingominer.services.oss import upload_file

openai_client = AsyncClient(
    base_url=config.llm_base_url,
    api_key=config.llm_api_key,
)


class FieldDefinition(BaseModel):
    name: str
    type: Literal["text", "audio", "image"]
    description: str


class Task(BaseModel):
    name: str
    action: str
    inputs: list[str]
    outputs: list[FieldDefinition]

    # Completion Task
    prompt: Optional[str] = None


class GenerationOutput(TypedDict):
    type: Literal["text", "audio", "image"]
    value: str | None


class State:
    def __init__(
        self, value: str | None = None, type: Literal["text", "audio", "image"] = "text"
    ):
        self.semaphore = asyncio.Semaphore(0)
        if value is not None:
            self.value = value
            self.type = type
            self.semaphore.release()
        else:
            self.value = None
            self.type = type

    def set(self, value: str):
        self.value = value
        self.semaphore.release()

    async def get(self) -> GenerationOutput:
        async with self.semaphore:
            return {"value": self.value, "type": self.type}


class Context:
    def __init__(self, context: dict = {}):
        self.context: dict[str, State] = {}
        self.init_keys = set(context.keys())
        for key, value in context.items():
            self.context[key] = State(value)

    def add(
        self,
        key: str,
        value: str | None = None,
        type: Literal["text", "audio", "image"] = "text",
    ):
        self.context[key] = State(value, type)

    async def get(self, key: str) -> GenerationOutput:
        if key not in self.context:
            raise ValueError(f"Key {key} not found in context")
        value = await self.context[key].get()
        return value

    def set(self, key: str, value: str):
        if key not in self.context:
            raise ValueError(f"Key {key} not found in context")
        self.context[key].set(value)

    def keys(self):
        return self.context.keys()

    def dump(self, exclude_init: bool = True) -> dict[str, GenerationOutput]:
        states = {
            key: {"value": state.value, "type": state.type}
            for key, state in self.context.items()
            if not exclude_init or key not in self.init_keys
        }
        return states

    def __str__(self):
        return str({key: state.value for key, state in self.context.items()})


class Flow:
    def __init__(self, context: Context = Context()):
        self.context = context
        self.actions: dict[str, Callable] = {}
        self.tasks: list[Task] = []
        # default actions
        self.add_action("completion", completion)
        self.add_action("toSpeech", toSpeech)
        self.add_action("toImage", toImage)

    def add_action(self, name: str, func: Callable):
        self.actions[name] = func

    def add_task(self, task: Task):
        for output in task.outputs:
            if output.name not in self.context.keys():
                self.context.add(key=output.name, type=output.type)
        self.tasks.append(task)

    async def _execute_task(self, task: Task):
        inputs: dict[str, GenerationOutput] = {}
        for input in task.inputs:
            inputs[input] = await self.context.get(input)
        outputs = await self.actions[task.action](self.context, task, inputs)
        for output in task.outputs:
            self.context.set(output.name, outputs[output.name]["value"])

    async def run(self, timeout: int | None = None):
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


async def completion(
    context: Context, task: Task, inputs: dict[str, GenerationOutput]
) -> dict[str, GenerationOutput]:
    for init_key in context.init_keys:
        inputs[init_key] = await context.get(init_key)
    response = await openai_client.chat.completions.create(
        model=config.llm_base_model,
        messages=[
            {
                "role": "system",
                "content": render_prompt(
                    task.prompt,
                    {k: v["value"] for k, v in inputs.items()},
                    task.outputs,
                ),
            },
        ],
        response_format={"type": "json_object"},
    )
    dict_result = json.loads(response.choices[0].message.content)
    logger.debug(f"Completion Result: {response.choices[0].message.content}")
    return {
        f.name: {
            "value": dict_result.get(f.name, None),
            "type": f.type,
        }
        for f in task.outputs
    }


async def toImage(
    context: Context, task: Task, inputs: dict[str, GenerationOutput]
) -> dict[str, GenerationOutput]:
    for init_key in context.init_keys:
        inputs[init_key] = await context.get(init_key)
    output_file_key = next(
        (output.name for output in task.outputs if output.type == "image"), None
    )
    if output_file_key is None:
        raise ValueError("toImage only support one image output")
    template = Template(task.prompt)
    prompt = template.render({k: v["value"] for k, v in inputs.items()})

    # result = await openai_client.images.generate(
    #     model="gpt-image-1",
    #     prompt=prompt,
    #     quality="low",
    #     size="256x256",
    # )
    result = await openai_client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="256x256",
        response_format="b64_json",
    )
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    # Save the image to a file
    with tempfile.TemporaryDirectory() as temp_dir:
        file_name = str(uuid.uuid4()) + ".png"
        file_path = os.path.join(temp_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        upload_file("lingominer", file_name, file_path)

    return {
        output_file_key: {
            "value": file_name,
            "type": "image",
        }
    }


async def toSpeech(
    context: Context, task: Task, inputs: dict[str, GenerationOutput]
) -> dict[str, GenerationOutput]:
    for init_key in context.init_keys:
        inputs[init_key] = await context.get(init_key)

    output_file_key = next(
        (output.name for output in task.outputs if output.type == "audio"), None
    )
    if output_file_key is None:
        raise ValueError("toSpeech only support one audio output")
    template = Template(task.prompt)
    text = template.render({k: v["value"] for k, v in inputs.items()})
    with tempfile.TemporaryDirectory() as temp_dir:
        file_name = str(uuid.uuid4()) + ".mp3"
        file_path = os.path.join(temp_dir, file_name)
        await generate_audio(text, file_path, "en-US-AvaMultilingualNeural")
        upload_file("lingominer", file_name, file_path)

    return {
        output_file_key: {
            "value": file_name,
            "type": "audio",
        }
    }


# async def lookup(inputs: dict) -> str:
#     if len(inputs) > 1:
#         raise ValueError("Lookup only support one input")
#     query = list(inputs.values())[0]
#     pass
