from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from lingominer.logger import logger

load_dotenv(override=True)
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LINGOMINER_")

    auth_key: str = Field(description="access key to lingominer api")

    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str
    llm_base_model: str = "deepseek-chat"

    jina_api_key: str

    database_host: Optional[str] = None
    database_port: Optional[int] = 3306
    database_user: Optional[str] = None
    database_password: Optional[str] = None
    database_db: Optional[str] = "lingominer"



config = Settings()

logger.debug(config.model_dump_json(indent=2))


PROJECT_DIR = Path(__file__).parent.parent
DATABASE_DIR = PROJECT_DIR / "database"

if not DATABASE_DIR.exists():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DICTIONARY_DIR = DATABASE_DIR / "dictionary.db"

AUDIO_DIR = DATABASE_DIR / "audio"

CARD_DEFAULT_FIELDS = ["paragraph", "decorated_paragraph"]
