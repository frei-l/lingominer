from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import Annotated

from lingominer.api.auth.security import get_current_user
from lingominer.database import get_db_session
from lingominer.models.user import User
from lingominer.ctx import user_id
from lingominer.api.auth.schemas import SettingsUpdate, UserDetail

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=UserDetail)
async def get_me(
    user: User = Depends(get_current_user),
):
    return user


@router.patch("/settings", response_model=UserDetail)
async def update_settings(
    settings: SettingsUpdate,
    db_session: Annotated[Session, Depends(get_db_session)],
):
    user = db_session.exec(select(User).where(User.id == user_id.get())).first()
    if settings.mochi_api_key:
        user.mochi_api_key = settings.mochi_api_key
    db_session.commit()
    return user
