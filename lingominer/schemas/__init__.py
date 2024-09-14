import pathlib
from sqlmodel import SQLModel, create_engine
from .mapping import Mapping
from .user import User
from .source import BrowserSelection
from .card import Card
from .integration import MochiConfig

# get project root dir using PATH
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()

__sqlite_file_name = "card.db"
__sqlite_url = f"sqlite:///{BASE_DIR}/{__sqlite_file_name}"
engine = create_engine(__sqlite_url, echo=False)