from fastapi import APIRouter, Depends
from sqlmodel import Session

from lingominer.auth.service import create
from lingominer.core.deps import get_current_user, get_db_session
from lingominer.schemas.user import User

router = APIRouter()


@router.post("/")
async def add_user(username: str, db_session: Session = Depends(get_db_session)):
    token = create(db_session, username)
    return {"token": token}


@router.get("/me")
async def get_user(user: User = Depends(get_current_user)):
    return {"username": user.username}
