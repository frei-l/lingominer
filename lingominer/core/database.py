from sqlmodel import SQLModel, create_engine
from lingominer import schemas
from lingominer.global_env import DB_DIR


engine = create_engine(DB_DIR, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
