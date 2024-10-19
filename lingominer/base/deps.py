from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from lingominer.auth.service import verify_user
from lingominer.base.database import engine
from lingominer.base.context_var import user_id_var

auth_scheme = HTTPBearer()


async def get_db_session():
    with Session(engine, autoflush=False) as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db_session: Session = Depends(get_db_session),
):
    user = verify_user(db_session, credentials.credentials)
    if user:
        user_id_var.set(user.id)
        return user
    raise HTTPException(status_code=401, detail="Invalid token")
