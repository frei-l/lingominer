from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from lingominer.schemas.card import Language
from lingominer.logger import logger
from lingominer.base.deps import get_current_user, get_db_session
from lingominer.schemas.user import User
from lingominer.schemas.mapping import Mapping

router = APIRouter()


@router.get("/")
async def get_mappings_view(
    lang: Language = Language.English,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    stmt = select(Mapping).where(Mapping.user_id == user.id, Mapping.lang == lang)
    mappings = db_session.exec(stmt).all()
    return mappings


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_mappings(
    data,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    pass
