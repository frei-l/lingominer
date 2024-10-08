from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from lingominer.auth.service import verify_user
from lingominer.core.database import engine
from lingominer.core.context_var import user_id

auth_scheme = HTTPBearer()


def get_db_session():
    with Session(engine, autoflush=False) as session:
        yield session


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db_session: Session = Depends(get_db_session),
):
    user = verify_user(db_session, credentials.credentials)
    if user:
        user_id.set(user.id)
        return user
    raise HTTPException(status_code=401, detail="Invalid token")
