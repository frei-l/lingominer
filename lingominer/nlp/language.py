from langfuse import Langfuse
from langfuse.model import ChatPromptClient
from langfuse.decorators import observe, langfuse_context

from functools import lru_cache
from pathlib import Path
from lingominer.schemas.source import BrowserSelection
from lingominer.schemas.card import CardBase, CardType
from lingominer.nlp.openai import llm_call
from lingominer.logger import logger

import requests
import sqlite3
import os
import re

READER_BASE_URL = "https://r.jina.ai/"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dictionary", "")

langfuse = Langfuse()
_language_register = {}


class BaseLanguage:
    lang = None
    lemmatize_prompt: ChatPromptClient = None
    summarize_prompt: ChatPromptClient = None
    lookup_prompt: ChatPromptClient = None
    simplify_prompt: ChatPromptClient = None
    segment_prompt: ChatPromptClient = None
    dictionary_path = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _language_register[cls.lang] = cls

    @classmethod
    def generate(cls, selection: BrowserSelection) -> CardBase:
        raise NotImplementedError("generate method is not implemented")

    @classmethod
    def explain(cls, word: str):
        """Get the explanation from local dictionary of the given word."""
        if cls is BaseLanguage:
            raise NotImplementedError("BaseLanguage is an abstract class")
        with sqlite3.connect(cls.dictionary_path) as db:
            cursor = db.cursor()
            cursor.execute("select * from dictionary WHERE entry=?;", (word,))
            value = cursor.fetchone()
            if not value:
                raise KeyError("entry not found in dictionary")
        # remove html tags
        entry = re.sub(r'<[^<]+?>', '', value[1])
        # remove extra spaces
        clean_entry = re.sub(r'\s+', ' ', entry)
        return clean_entry

    @classmethod
    def frequncy(cls, word: str):
        """Get the frequency of the given word."""
        if cls is BaseLanguage:
            raise NotImplementedError("BaseLanguage is an abstract class")
        with sqlite3.connect(cls.dictionary_path) as db:
            cursor = db.cursor()
            cursor.execute("select * from frequency WHERE lemma=?;", (word,))
            value = cursor.fetchone()
            if not value:
                raise KeyError("entry not found in frequency dictionary")
        return value[1]

    @classmethod
    def simplify(cls, sentence: str, word: str):
        """rephrase the raw sentence with simple words"""
        if cls is BaseLanguage:
            raise NotImplementedError("BaseLanguage is an abstract class")
        return llm_call(cls.simplify_prompt, sentence=sentence, word=word)

    @classmethod
    def lemmatize(cls, sentence: str, word: str):
        """Lemmatize the given word within the context of the sentence."""
        if cls is BaseLanguage:
            raise NotImplementedError("BaseLanguage is an abstract class")
        return llm_call(cls.lemmatize_prompt, sentence=sentence, word=word)

    @classmethod
    def segment(cls, text: str, start: int, end: int) -> str:
        """Segment the text starting from the given position."""
        if cls is BaseLanguage:
            raise NotImplementedError("BaseLanguage is an abstract class")
        decorated_text = text[:start] + "**" + text[start:end] + "**" + text[end:]
        return llm_call(cls.segment_prompt, paragraph=decorated_text)

    @classmethod
    def lookup(cls, sentence: str, word: int, dictionary: int) -> str:
        """Segment the text starting from the given position."""
        if cls is BaseLanguage:
            raise NotImplementedError("BaseLanguage is an abstract class")
        return llm_call(cls.lookup_prompt, sentence=sentence, word=word, dictionary=dictionary)

    @classmethod
    @lru_cache(maxsize=32)
    def summarize(cls, target_url: str) -> str:
        """Summarize the content of the given URL."""
        if cls is BaseLanguage:
            raise NotImplementedError("BaseLanguage is an abstract class")
        reader_response = requests.get(READER_BASE_URL + target_url)
        return llm_call(cls.summarize_prompt, context=reader_response.text)


class German(BaseLanguage):
    lang = 'de'
    lemmatize_prompt = langfuse.get_prompt(f"{lang}.lemmatize")
    summarize_prompt = langfuse.get_prompt(f"{lang}.summarize")
    lookup_prompt = langfuse.get_prompt(f"{lang}.lookup")
    simplify_prompt = langfuse.get_prompt(f"{lang}.simplify")
    segment_prompt = langfuse.get_prompt(f"{lang}.segment")
    dictionary_path = (
        Path(__file__).parents[1] / "dictionary" / lang / "dictionary.db"
    )

    @classmethod
    @observe()
    def generate(cls, bs: BrowserSelection) -> CardBase:
        langfuse_context.update_current_observation(
            name="German card generation"
        )
        selection = bs.text[bs.start:bs.end]
        if len(selection.split(" ")) > 1:
            card_type = CardType.expression
            raise NotImplementedError("expression is not implemented: "+selection)
        else:
            card_type = CardType.singleWord
            word = selection
        sentence = cls.segment(bs.text, bs.start, bs.end)
        logger.info(f"sentence: {sentence}")

        lemma = cls.lemmatize(sentence, word)
        logger.info(f"lemma: {lemma}")

        summary = cls.summarize(bs.url)
        logger.info(f"summary: {summary}")

        frequency = cls.frequncy(lemma)
        logger.info(f"frequency: {frequency}")

        entry = cls.explain(lemma)
        logger.info(f"entry: {entry}")

        explanation = cls.lookup(sentence, word, entry)
        logger.info(f"explanation: {explanation}")

        simple_sentence = cls.simplify(sentence, word)
        logger.info(f"simple_sentence: {simple_sentence}")

        return CardBase(
            type=card_type,
            lang=cls.lang,
            selection=selection,
            word=word,
            lemma=lemma,
            frequency=frequency,
            explanation=explanation,
            sentence=sentence,
            simple_sentence=simple_sentence,
            expression=lemma,
            pos_start=bs.start,
            pos_end=bs.end,
            paragraph=bs.text,
            summary=summary,
            url=bs.url
        )

        
def load(language: str) -> BaseLanguage:
    try:
        return _language_register[language]
    except KeyError:
        raise ValueError(f"Unsupported language: {language}")


__all__ = [
    "load",
    "BaseLanguage",
    "German"
]
