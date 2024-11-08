import re
import sqlite3
from functools import lru_cache

from lingominer.global_env import DICTIONARY_DIR
from lingominer.logger import logger
from lingominer.nlp.langfuse import ChatPromptClient, langfuse, observe
from lingominer.nlp.openai import llm_call
from lingominer.nlp.jina import scrape_url
from lingominer.schemas import BrowserSelection, CardBase


class BaseLanguage:
    _language_register = {}
    lemmatize_prompt: ChatPromptClient = langfuse.get_prompt("base.lemmatize")
    summarize_prompt: ChatPromptClient = langfuse.get_prompt("base.summarize")
    lookup_prompt: ChatPromptClient = langfuse.get_prompt("base.lookup")
    simplify_prompt: ChatPromptClient = langfuse.get_prompt("base.simplify")
    segment_prompt: ChatPromptClient = langfuse.get_prompt("base.segment")
    preprocess_prompt: ChatPromptClient = langfuse.get_prompt("base.generate")

    def __init_subclass__(cls, lang: str, **kwargs):
        super().__init_subclass__(**kwargs)
        logger.info(f"register language: {cls.__name__}")
        cls.lang = lang
        cls._language_register[lang] = cls

    @classmethod
    @observe()
    def generate(cls, selection: BrowserSelection) -> CardBase:
        if selection.lang not in cls._language_register:
            raise ValueError(
                f"Language {selection.lang} not supported, now only support {cls._language_register.keys()}"
            )
        parser: BaseLanguage = cls._language_register[selection.lang]
        return parser.generate(selection)

    @classmethod
    @observe()
    def preprocess(cls, text: str, start: int, end: int) -> dict:
        """Preprocess the selection before generating the note."""
        decorated_text = text[:start] + "**" + text[start:end] + "**" + text[end:]
        return llm_call(cls.preprocess_prompt, text=decorated_text)

    @classmethod
    def explain(cls, word: str):
        """Get the explanation from local dictionary of the given word."""
        with sqlite3.connect(DICTIONARY_DIR) as db:
            cursor = db.cursor()
            cursor.execute(f"select * from {cls.lang}_dict WHERE entry=?;", (word,))
            value = cursor.fetchone()
            if not value:
                raise KeyError("entry not found in dictionary")
        # remove html tags
        entry = re.sub(r"<[^<]+?>", "", value[1])
        # remove extra spaces
        clean_entry = re.sub(r"\s+", " ", entry)
        return clean_entry

    @classmethod
    def frequncy(cls, word: str):
        """Get the frequency of the given word."""
        with sqlite3.connect(DICTIONARY_DIR) as db:
            cursor = db.cursor()
            cursor.execute(f"select * from {cls.lang}_freq WHERE lemma=?;", (word,))
            value = cursor.fetchone()
            if not value:
                raise KeyError("entry not found in frequency dictionary")
        return value[1]

    @classmethod
    def simplify(cls, sentence: str, word: str):
        """rephrase the raw sentence with simple words"""
        return llm_call(cls.simplify_prompt, sentence=sentence, word=word)

    @classmethod
    def lemmatize(cls, sentence: str, word: str):
        """Lemmatize the given word within the context of the sentence."""
        return llm_call(cls.lemmatize_prompt, sentence=sentence, word=word)

    @classmethod
    def segment(cls, text: str, start: int, end: int) -> str:
        """Segment the text starting from the given position."""
        decorated_text = (
            text[:start] + "<word>" + text[start:end] + "</word>" + text[end:]
        )
        return llm_call(cls.segment_prompt, paragraph=decorated_text)

    @classmethod
    def lookup(cls, sentence: str, word: int, dictionary: int) -> str:
        """Lookup the given word in the dictionary."""
        return llm_call(
            cls.lookup_prompt, sentence=sentence, word=word, dictionary=dictionary
        )

    @classmethod
    @lru_cache(maxsize=32)
    def summarize(cls, target_url: str) -> str:
        """Summarize the content of the given URL."""
        return llm_call(cls.summarize_prompt, website=scrape_url(target_url))


def generate_note(selection: BrowserSelection):
    return BaseLanguage.generate(selection)


from lingominer.nlp.plugin import english, german
