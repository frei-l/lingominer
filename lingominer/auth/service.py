from lingominer.logger import logger
from lingominer.schemas.user import User


from sqlmodel import Session, select


from hashlib import sha256
from secrets import token_urlsafe
import os


def create(db_session: Session, username: str):
    token = "sk_" + token_urlsafe(16)
    # hash token use passlib
    user = User(username=username, hash_token=sha256(token.encode()).hexdigest())
    db_session.add(user)
    db_session.commit()
    return token


def verify_user(db_session: Session, token: str):
    if os.getenv("DEV") and not token:
        token = os.getenv("DEV_API_KEY")
    logger.info(f"verify user: {token}")
    stmt = select(User).where(User.hash_token == sha256(token.encode()).hexdigest())
    user = db_session.exec(stmt).first()
    logger.info(f"user: {user}")
    if user:
        return user
    return None
