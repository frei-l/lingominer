from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from lingominer.ctx import user_id
from lingominer.database import get_db_session
from lingominer.models.passage import Passage
from lingominer.services.ai import openai_client
from lingominer.services.jina import scrape_url
from lingominer.api.auth.security import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("", response_model=Passage)
async def create_passage(url: str, db: Session = Depends(get_db_session)):
    prompt = """
    I will provide you with raw web content enclosed in <original_raw_text> tags. 
    Please transform this content into a well-formatted, reader-friendly text following these specifications:

    Format:
    - Use proper Markdown syntax
    - Begin with a main title using "# Title" format
    - Organize content into clear, coherent paragraphs
    Paragraph Structure:
    - Each paragraph should contain 2-5 sentences
    - Maintain optimal paragraph length (roughly 50-100 words)
    - Ensure smooth transitions between paragraphs
    - Use appropriate line breaks between paragraphs
    Text Cleaning:
    - Remove all HTML tags and formatting
    - Eliminate redundant spaces and line breaks
    - Fix any typographical or formatting errors
    - Preserve only meaningful content
    Output Requirements:
    - Produce clean, professional-grade text
    - Maintain the original message and key information, wording.
    - Format suitable for print publication (books, newspapers, etc.)
    - Ensure logical flow and readability

    Please process the content to meet these requirements while preserving the essential information and meaning of the original text.
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": prompt
                + "<original_raw_text>"
                + scrape_url(url)
                + "</original_raw_text>",
            },
        ],
    )
    content = response.choices[0].message.content

    title = content.split("\n")[0].removeprefix("# ")

    passage = Passage(
        title=title,
        url=url,
        content=content,
        user_id=user_id.get(),
    )
    db.add(passage)
    db.commit()
    db.refresh(passage)
    return passage


@router.get("", response_model=list[Passage])
async def get_passages(db: Session = Depends(get_db_session)):
    passages = db.exec(
        select(Passage).where(Passage.user_id == user_id.get()).limit(5)
    ).all()
    return passages
