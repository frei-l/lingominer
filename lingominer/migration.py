from lingominer.schemas import engine
from sqlmodel import SQLModel

if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
