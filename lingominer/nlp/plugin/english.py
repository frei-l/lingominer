from lingominer.nlp.language import BaseLanguage
from lingominer.logger import logger
from lingominer.schemas import BrowserSelection, CardBase, CardType
from lingominer.nlp.langfuse import langfuse, langfuse_context, observe


class English(BaseLanguage, lang="en"):
    voice_code = "en-US-AndrewMultilingualNeural"

    @classmethod
    def frequncy(cls, word: str):
        return 1

    @classmethod
    @observe()
    def generate(cls, bs: BrowserSelection) -> CardBase:
        langfuse_context.update_current_observation(name="English card generation")
        basic_info = cls.preprocess(bs.text, bs.start, bs.end)

        selection = bs.text[bs.start : bs.end]
        word = basic_info["word"]
        sentence = basic_info["sentence"]
        expression = basic_info["expression"]
        lemma = None

        if len(basic_info["expression"]) > 1:
            card_type = CardType.expression
        else:
            card_type = CardType.singleWord

        for lemma in basic_info["lemma"]:
            entries = {}
            try:
                entry = cls.explain(lemma)
                entries[lemma] = entry
            except KeyError:
                logger.warning(f"entry not found for lemma: {lemma}")
        if entries:
            # if entry is not empty, get longest one
            longest_key = max(entries, key=lambda k: len(entries[k]))
            lemma = longest_key
            entry = entries[longest_key]
        else:
            # if no entry found, use the shortest key as lemma
            lemma = min(basic_info["lemma"], key=len)
            entry = None

        summary = cls.summarize(bs.url)
        logger.info(f"summary: {summary}")

        frequency = cls.frequncy(lemma)
        logger.info(f"frequency: {frequency}")

        explanation = cls.lookup(sentence, word, entry)
        logger.info(f"explanation: {explanation}")

        simple_sentence = cls.simplify(sentence, expression)
        logger.info(f"simple_sentence: {simple_sentence}")

        simple_sentence_audio = cls.tts(simple_sentence.replace("==", ""))
        logger.info(f"simple_sentence_audio: {simple_sentence_audio}")

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
            simple_sentence_audio=f"![simple_sentence]({simple_sentence_audio})",
            expression=expression,
            pos_start=bs.start,
            pos_end=bs.end,
            paragraph=bs.text,
            summary=summary,
            url=bs.url,
        )
