from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from lingominer.api.auth.security import get_current_user
from lingominer.api.passages.schemas import (
    NoteCreate,
    NoteDetail,
    PassageDetail,
    PassageList,
)
from lingominer.ctx import user_id
from lingominer.database import get_db_session
from lingominer.models.passage import Note, Passage
from lingominer.services.ai import openai_client
from lingominer.services.jina import scrape_url

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("", response_model=PassageDetail)
async def create_passage(url: str, session: Session = Depends(get_db_session)):
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
    session.add(passage)
    session.commit()
    session.refresh(passage)
    return passage


@router.get("", response_model=list[PassageList])
async def get_passages(db: Session = Depends(get_db_session)):
    passages = db.exec(
        select(Passage).where(Passage.user_id == user_id.get()).limit(5)
    ).all()
    return passages


@router.get("/{passage_id}", response_model=PassageDetail)
async def get_passage(passage_id: str, session: Session = Depends(get_db_session)):
    passage = session.exec(
        select(Passage)
        .where(Passage.id == passage_id)
        .where(Passage.user_id == user_id.get())
    ).one_or_none()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    return passage


@router.post("/{passage_id}/notes", response_model=NoteDetail)
async def create_note(
    passage_id: str, note_create: NoteCreate, session: Session = Depends(get_db_session)
):
    prompt = f"""
    in the context of the following text, 
    please explain the meaning of the selected text in a way that is easy to understand.
    The explanation should be concise and to the point, and should be less then 3 sentences.
    explain in Chinese.
    <text>
    {note_create.context}
    </text>
    <selected_text>
    {note_create.selected_text}
    </selected_text>
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    note = Note(
        user_id=user_id.get(),
        passage_id=passage_id,
        content=response.choices[0].message.content,
        selected_text=note_create.selected_text,
        context=note_create.context,
        paragraph_index=note_create.paragraph_index,
        start_index=note_create.start_index,
        end_index=note_create.end_index,
    )

    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.delete("/{passage_id}", status_code=200)
async def delete_passage(
    passage_id: str,
    db_session: Annotated[Session, Depends(get_db_session)],
):
    # delete all notes for the passage
    notes = db_session.exec(
        select(Note)
        .where(Note.passage_id == passage_id)
        .where(Note.user_id == user_id.get())
    ).all()
    for note in notes:
        db_session.delete(note)
    db_session.commit()

    passage = db_session.exec(
        select(Passage)
        .where(Passage.id == passage_id)
        .where(Passage.user_id == user_id.get())
    ).one_or_none()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    db_session.delete(passage)
    db_session.commit()
    return {"message": "Passage deleted successfully"}
