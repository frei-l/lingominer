from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lingominer.auth.view import router as auth_router
from lingominer.cards.view import router as cards_router
from lingominer.mappings.view import router as mappings_router
from lingominer.mochi.view import router as mochi_router


app = FastAPI(title="api")

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(cards_router, prefix="/cards", tags=["cards"])
app.include_router(mappings_router, prefix="/mappings", tags=["mappings"])
app.include_router(mochi_router, prefix="/mochi", tags=["mochi"])
