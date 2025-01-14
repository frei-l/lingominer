from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lingominer.database import get_db_session

# from lingominer.cards.view import router as cards_router


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


# app.include_router(cards_router, prefix="/cards", tags=["cards"])
