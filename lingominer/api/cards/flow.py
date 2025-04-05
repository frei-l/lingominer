import asyncio

from lingominer.services.ai import openai_client


async def detect_language(text: str) -> str:
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"detect the language of the following text: <text>{text}</text> Your should be return the language in ISO 639-1 format, for example: en, zh, ja, etc.",
            }
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(asyncio.run(detect_language("Hello, world!")))
