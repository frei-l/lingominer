import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from lingominer.core.deps import get_current_user, get_db_session
from lingominer.mochi import service as db
from lingominer.schemas.integration import MochiConfigCreate

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def add_mochi_config(
    config: MochiConfigCreate,
    db_session: Session = Depends(get_db_session),
):
    config_id = db.create(db_session, config)
    return {"config_id": config_id}


@router.get("/", dependencies=[Depends(get_current_user)])
async def get_mochi_configs_views(
    db_session: Session = Depends(get_db_session),
):
    configs = db.get(db_session)
    return {"configs": configs}


@router.get("/{config_id}", dependencies=[Depends(get_current_user)])
async def get_mochi_config(
    config_id: uuid.UUID,
    db_session: Session = Depends(get_db_session),
):
    config = db.get_by_id(db_session, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Mochi config not found")
    return config
