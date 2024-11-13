from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DATABASE_DIR = PROJECT_DIR / "database"
DICTIONARY_DIR = DATABASE_DIR / "dictionary.db"
DB_DIR = DATABASE_DIR / "lingominer.db"
CHROMA_DIR = DATABASE_DIR / "chroma"
AUDIO_DIR = DATABASE_DIR / "audio"
