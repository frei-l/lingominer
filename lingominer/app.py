from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from lingominer.api.cards.view import router as cards_router
from lingominer.api.passages.view import router as passages_router
from lingominer.api.templates.view import router as templates_router
from lingominer.api.users.view import router as users_router
from lingominer.api.auth.views import router as auth_router
from lingominer.api.mochi.view import router as mochi_router
from lingominer.database import get_db_session
from lingominer.logger import logger

app = FastAPI(
    title="api",
)

app.include_router(templates_router, prefix="/templates", tags=["templates"])
app.include_router(cards_router, prefix="/cards", tags=["cards"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(passages_router, prefix="/passages", tags=["passages"])
app.include_router(auth_router, prefix="/me", tags=["me"])
app.include_router(mochi_router, prefix="/mochi", tags=["mochi"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    # logger.error(f"Exception occurred: {exc}")
    return JSONResponse(status_code=500, content={"error": str(exc)})
