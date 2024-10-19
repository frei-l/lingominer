from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from lingominer.logger import logger
from lingominer.base.deps import get_current_user, get_db_session
from lingominer.mappings import service as db
from lingominer.schemas.user import User

router = APIRouter()


@router.get("/")
async def get_mappings_view(
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    mappings = db.get(db_session, user)
    return {"mappings": mappings}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_mappings(
    data,
    db_session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    pass
