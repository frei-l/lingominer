from lingominer.nlp.language import BaseLanguage
from lingominer.logger import logger
from lingominer.schemas import BrowserSelection, CardBase, CardType
from lingominer.nlp.langfuse import langfuse, langfuse_context, observe


class German(BaseLanguage, lang="de"):
    lemmatize_prompt = langfuse.get_prompt("de.lemmatize")
    summarize_prompt = langfuse.get_prompt("de.summarize")
    lookup_prompt = langfuse.get_prompt("de.lookup")
    simplify_prompt = langfuse.get_prompt("de.simplify")
    segment_prompt = langfuse.get_prompt("de.segment")

    @classmethod
    @observe()
    def generate(cls, bs: BrowserSelection) -> CardBase:
        langfuse_context.update_current_observation(name="German card generation")
        selection = bs.text[bs.start : bs.end]
        if len(selection.split(" ")) > 1:
            card_type = CardType.expression
            raise NotImplementedError("expression is not implemented: " + selection)
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
            url=bs.url,
        )
