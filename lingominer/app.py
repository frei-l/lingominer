from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from lingominer.api.templates.view import router as templates_router
from lingominer.database import get_db_session
from lingominer.logger import logger

# from lingominer.cards.view import router as cards_router


app = FastAPI(
    title="api",
)

app.include_router(templates_router, prefix="/templates", tags=["templates"])
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
