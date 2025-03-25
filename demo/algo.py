import asyncio
import os
import json
from dataclasses import dataclass
from typing import Any, Callable, Optional, Literal

from dotenv import load_dotenv
from jinja2 import Template
from openai import AsyncClient
import pprint

load_dotenv()

openai_client = AsyncClient(
    base_url=os.getenv("LINGOMINER_LLM_BASE_URL"), api_key=os.getenv("LINGOMINER_LLM_API_KEY")
)


@dataclass
class FieldDefinition:
    name: str
    type: Literal["text", "audio"]
    description: str


@dataclass
class Task:
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

    def __str__(self):
        return str({key: state.value for key, state in self.context.items()})


class Flow:
    def __init__(self, context: Context = Context()):
        self.context = context
        self.actions: dict[str, Callable] = {}
        self.tasks: list[Task] = []

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

    async def run(self):
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
    return final_prompt


async def completion(context: Context, task: Task, inputs: dict) -> dict:
    response = await openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": render_prompt(task.prompt, inputs, task.outputs),
            },
        ],
        response_format={"type": "json_object"},
    )
    dict_result = json.loads(response.choices[0].message.content)
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


async def main():
    context_dict = {
        "text": "In addition to its rings, Saturn has 25 satellites that measure at least 6 miles (10 kilometers) in diameter, and several smaller satellites. The largest of Saturn’s satellites, Titan, has a diameter of about 3,200 miles—larger than the planets Mercury and Pluto. Titan is one of the few satellites in the solar system known to have an atmosphere. Its atmosphere consists largely of nitrogen. Many of Saturn’s satellites have large **craters**. For example, Mimas has a crater that covers about one-third the diameter of the satellite.",
    }
    g1 = Task(
        name="extract_target",
        action="completion",
        inputs=["text"],
        outputs=[
            FieldDefinition(
                name="word",
                type="text",
                description="The target word to be extracted",
            ),
            FieldDefinition(
                name="sentence",
                type="text",
                description="The sentence containing the target word",
            ),
        ],
        prompt=(
            "Giving a paragraph, extract the target word and the sentence. "
            "the target word is highlighted with **, the sentence is the sentence containing the target word."
            "the text is: '{{text}}'"
        ),
    )
    g2 = Task(
        name="extract_lemma",
        action="completion",
        inputs=["word"],
        outputs=[
            FieldDefinition(
                name="lemma", type="text", description="The lemma of the word"
            )
        ],
        prompt="Extract the lemma of the word. The lemma is the base form of the word. The word is: '{{word}}'",
    )
    g3 = Task(
        name="explain_word",
        action="completion",
        inputs=["lemma", "sentence"],
        outputs=[
            FieldDefinition(
                name="pronunciation",
                type="text",
                description="The pronunciation of the word",
            ),
            FieldDefinition(
                name="explanation",
                type="text",
                description="The explanation of the word",
            ),
        ],
        prompt=(
            "Explain the word in the sentence. tell me the pronunciation and the explanation of the word. "
            "the word is: '{{word}}' "
            "the sentence is: '{{sentence}}'"
        ),
    )
    g4 = Task(
        name="summarize",
        action="completion",
        inputs=["text"],
        outputs=[
            FieldDefinition(
                name="summary",
                type="text",
                description="The summary of the text",
            )
        ],
        prompt="Summarize the text. The text is: '{{text}}'",
    )
    g5 = Task(
        name="simplify",
        action="completion",
        inputs=["sentence"],
        outputs=[
            FieldDefinition(
                name="simple_sentence",
                type="text",
                description="The simplified sentence",
            )
        ],
        prompt="Simplify the sentence. The sentence is: '{{sentence}}'",
    )

    context = Context(context_dict)
    flow = Flow(context)
    flow.add_action("completion", completion)
    flow.add_task(g1)
    flow.add_task(g2)
    flow.add_task(g3)
    flow.add_task(g4)
    flow.add_task(g5)
    result = await flow.run()
    pprint.pprint(result.context)


if __name__ == "__main__":
    asyncio.run(main())
