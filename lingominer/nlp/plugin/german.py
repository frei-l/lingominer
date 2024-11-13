from lingominer.nlp.language import BaseLanguage
from lingominer.logger import logger
from lingominer.schemas import BrowserSelection, CardBase, CardType
from lingominer.nlp.langfuse import langfuse, langfuse_context, observe


class German(BaseLanguage, lang="de"):
    summarize_prompt = langfuse.get_prompt("de.summarize")
    lookup_prompt = langfuse.get_prompt("de.lookup")
    simplify_prompt = langfuse.get_prompt("de.simplify")

    @classmethod
    @observe()
    def generate(cls, bs: BrowserSelection) -> CardBase:
        pass
