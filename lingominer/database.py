from sqlmodel import Session, create_engine

import lingominer.models as models  # noqa
from lingominer.config import config


def init_database_engine():
    engine = create_engine(
        f"postgresql+psycopg://{config.database_user}:{config.database_password}@{config.database_host}:{config.database_port}/{config.database_db}",
        echo=False,
    )

    return engine


engine = init_database_engine()


async def get_db_session():
    with Session(engine, autoflush=False) as session:
        yield session
