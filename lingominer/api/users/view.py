import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from lingominer.api.auth.security import get_admin
from lingominer.database import get_db_session
from lingominer.models.user import ApiKey, User

router = APIRouter(dependencies=[Depends(get_admin)])


@router.get("")
async def get_users(
    db_session: Annotated[Session, Depends(get_db_session)],
):
    return db_session.exec(select(User)).all()


@router.post("")
async def create_user(
    db_session: Annotated[Session, Depends(get_db_session)],
    name: str,
):
    user = User(name=name)
    db_session.add(user)
    db_session.commit()
    return user


@router.get("/{user_id}")
async def get_user(
    db_session: Annotated[Session, Depends(get_db_session)],
    user_id: str,
):
    return db_session.exec(select(User).where(User.id == user_id)).first()


@router.delete("/{user_id}")
async def delete_user(
    db_session: Annotated[Session, Depends(get_db_session)],
    user_id: str,
):
    user = db_session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_session.delete(user)
    db_session.commit()
    return {"message": "User deleted"}


@router.get("/{user_id}/api-keys")
async def get_api_keys(
    db_session: Annotated[Session, Depends(get_db_session)],
    user_id: str,
):
    return db_session.exec(select(ApiKey).where(ApiKey.user_id == user_id)).all()


@router.post("/{user_id}/api-keys")
async def create_api_key(
    db_session: Annotated[Session, Depends(get_db_session)],
    user_id: str,
):
    api_key = ApiKey(key=f"sk-{uuid.uuid4().hex}{uuid.uuid4().hex}", user_id=user_id)
    db_session.add(api_key)
    db_session.commit()
    return {"key": api_key.key}


@router.delete("/users/{user_id}/api-keys/{api_key_id}")
async def delete_api_key(
    db_session: Annotated[Session, Depends(get_db_session)],
    user_id: str,
    api_key_id: str,
):
    api_key = db_session.exec(
        select(ApiKey).where(ApiKey.id == api_key_id, ApiKey.user_id == user_id)
    ).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    db_session.delete(api_key)
    db_session.commit()
    return {"message": "API key deleted"}
