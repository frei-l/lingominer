from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from lingominer.database import get_db_session
from sqlmodel import Session, select
from lingominer.models.user import User
from lingominer.config import config
from lingominer.ctx import user_id

auth_scheme = HTTPBearer()


async def get_current_user(
    db_session: Annotated[Session, Depends(get_db_session)],
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> User:
    user = db_session.exec(
        select(User).where(User.api_keys.any(key=credentials.credentials))
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id.set(user.id)
    return user


async def get_admin(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> User:
    if credentials.credentials != config.auth_key:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id.set("system")
    return User(id="system", name="System")
