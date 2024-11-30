import os

from sqlmodel import SQLModel, create_engine
from lingominer import schemas
from lingominer.global_env import DB_DIR

# Create a SQLite engine based on a local file
if os.environ.get("LINGOMINER_DB_TYPE") == "sqlite":
    engine = create_engine(f"sqlite:///{DB_DIR.as_posix()}", echo=False)
else:
    host = os.environ.get("LINGOMINER_DB_HOST")
    port = os.environ.get("LINGOMINER_DB_PORT")
    user = os.environ.get("LINGOMINER_DB_USER")
    password = os.environ.get("LINGOMINER_DB_PASSWORD")
    db_name = os.environ.get("LINGOMINER_DB_NAME")
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}", echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
