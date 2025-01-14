from sqlmodel import Session, SQLModel, create_engine
from lingominer.models import *
from lingominer.logger import logger
from lingominer.config import config, DB_DIR


def init_sqlite_engine():
    if not DB_DIR.exists():
        logger.info(f"Creating sqlite database at {DB_DIR.as_posix()}")
        engine = create_engine(f"sqlite:///{DB_DIR.as_posix()}", echo=False)
        SQLModel.metadata.create_all(engine)
    else:
        engine = create_engine(f"sqlite:///{DB_DIR.as_posix()}", echo=False)

    return engine


def init_mysql_engine():
    # First create engine without database to check if db exists
    temp_engine = create_engine(
        f"mysql+pymysql://{config.mysql_user}:{config.mysql_password}@{config.mysql_host}:{config.mysql_port}",
        echo=False,
    )

    with temp_engine.connect() as conn:
        # Check if database exists
        result = conn.execute(f"SHOW DATABASES LIKE '{config.mysql_db}'")
        db_exists = result.fetchone() is not None

        if not db_exists:
            logger.info(f"Creating mysql database {config.mysql_db} at {config.mysql_host}:{config.mysql_port}")
            conn.execute(f"CREATE DATABASE {config.mysql_db}")

    # Create final engine with database
    engine = create_engine(
        f"mysql+pymysql://{config.mysql_user}:{config.mysql_password}@{config.mysql_host}:{config.mysql_port}/{config.mysql_db}",
        echo=False,
    )

    if not db_exists:
        SQLModel.metadata.create_all(engine)

    return engine


# Create engine based on configuration
if config.mysql_host is None:
    engine = init_sqlite_engine()
else:
    engine = init_mysql_engine()


async def get_db_session():
    with Session(engine, autoflush=False) as session:
        yield session
