from typing import Optional
from pathlib import Path

from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict
from lingominer.logger import logger


class Settings(BaseSettings):
    auth_key: str = Field(description="access key to lingominer api")

    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str
    llm_base_model: str = "deepseek-chat"

    mysql_host: Optional[str] = None
    mysql_port: Optional[int] = 3306
    mysql_user: Optional[str] = None
    mysql_password: Optional[str] = None
    mysql_db: Optional[str] = "lingominer"

    model_config = SettingsConfigDict(env_prefix="LINGOMINER_")


config = Settings()

logger.debug(config.model_dump_json(indent=2))


PROJECT_DIR = Path(__file__).parent.parent
DATABASE_DIR = PROJECT_DIR / "database"

DICTIONARY_DIR = DATABASE_DIR / "dictionary.db"
DB_DIR = DATABASE_DIR / "lingominer.db"

CHROMA_DIR = DATABASE_DIR / "chroma"
AUDIO_DIR = DATABASE_DIR / "audio"

CARD_DEFAULT_FIELDS = ["paragraph", "decorated_paragraph"]
