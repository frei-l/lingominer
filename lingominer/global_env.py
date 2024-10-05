from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DICTIONARY_DIR = PROJECT_DIR / "database" / "dictionary.db"
DB_DIR = PROJECT_DIR / "database" / "lingominer.db"
CHROMA_DIR = PROJECT_DIR / "database" / "chroma"

print(CHROMA_DIR.as_posix())