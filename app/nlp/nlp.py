from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from functools import lru_cache
from dotenv import load_dotenv
from pathlib import Path
from ..type import BrowserSelection, BaseCard
import requests
import os
import sqlite3

load_dotenv()
READER_BASE_URL = "https://r.jina.ai/"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dictionary", "")


class BaseLanguage:
    def __init__(self) -> None:
        self.lang = None
        self.lemmatizer = None
        self.summarizer = None
        self.segmenter = None
        self.simplifier = None
        self.dictionary_path = None

    def generate(self, selection: BrowserSelection) -> BaseCard:

        pass

    def explain(self, word: str):
        with sqlite3.connect(self.dictionary_path) as db:
            cursor = db.cursor()
            cursor.execute("select * from dictionary WHERE entry=?;", (word,))
            value = cursor.fetchone()
            if not value:
                raise KeyError("entry not found in dictionary")
        return value[1]

    def frequncy(self, word: str):
        with sqlite3.connect(self.dictionary_path) as db:
            cursor = db.cursor()
            cursor.execute("select * from frequency WHERE lemma=?;", (word,))
            value = cursor.fetchone()
            if not value:
                raise KeyError("entry not found in frequency dictionary")
        return value[1]

    def reduce_explanations(self, sentence: str, word: str, explanations: str):
        pass

    def simplify(self, sentence: str, word: str):
        """rephrase the raw sentence with simple words"""
        return self.simplifier.invoke({"sentence": sentence, "word": word})

    def lemmatize(self, sentence: str, word: str):
        """Lemmatize the given word within the context of the sentence."""
        return self.lemmatizer.invoke({"sentence": sentence, "word": word})

    def segment(self, text: str, start: int, end: int) -> str:
        """Segment the text starting from the given position."""
        return self.segmenter.invoke({"paragraph": text, "start": start, "end": end})

    @lru_cache(maxsize=32)
    def summarize(self, target_url: str) -> str:
        """Summarize the content of the given URL."""
        reader_response = requests.get(READER_BASE_URL + target_url)
        return self.summarizer.invoke({"context": reader_response.text})


class German(BaseLanguage):
    def __init__(self) -> None:
        super().__init__()
        self.lang = "de"
        self.dictionary_path = (
            Path(__file__).parents[1] / "dictionary" / self.lang / "dictionary.db"
        )

        # initialize lemmatizer
        gpt4 = ChatOpenAI(
            api_key=os.getenv("api_key"),
            base_url=os.getenv("base_url"),
            model="gpt-4-turbo",
        )
        lemmatize_prompt = PromptTemplate.from_template(
            """
            ###Instruction###
            You are a German linguist tasked with annotating the morphological structure of words. 
            I will provide you with a sentence and a specific word from that sentence. 
            Your task is to identify and respond with the lemma (dictionary form) of the given word.
            ###Details###
            If the word is part of a separable verb, provide the lemma of the complete verb.
            Your response should only contain the lemma, without any additional commentary or explanations.
            Focus on providing a concise and accurate response.
            ###Question###
            <text>{sentence}</text> 
            word: "{word}"
            """
        )
        parser = StrOutputParser()
        self.lemmatizer = lemmatize_prompt | gpt4 | parser

        # initialize segmenter
        segmentation_prompt = PromptTemplate.from_template(
            """
            ###Instruction###
            You are a German linguist tasked with identifying and extracting sentences containing a specific target word from a paragraph.
            The target word will be indicated by the offset of the target word in paragraph.
            Carefully analyze each sentence, considering grammar and punctuation, to ensure accurate extraction based on the boundaries of the sentences.
            ###Example###
            input: <text>Tagelang hocken sie in Kellern und steuern tödliche Waffen. Die Männer einer ukrainischen Drohneneinheit leben mit der ständigen Angst, entdeckt zu werden. Doch besonders groß ist ihre Furcht vor etwas anderem</text>
            index: 23-30
            output: Tagelang hocken sie in Kellern und steuern tödliche Waffen.
            ###Question###
            <text>{paragraph}</text>
            index: {start}-{end}
            """
        )
        self.segmenter = segmentation_prompt | gpt4 | parser

        # initialize simplifier
        simplify_prompt = PromptTemplate.from_template(
            """
            ###Instruction###
            You are playing the role of a language teacher tasked with simplifying complex sentences for foreign language learners. 
            The goal is to make the sentence as simple and short as possible while preserving the form and meaning of the specified word. 
            You should meanwhile tag the word in new sentence, including auxillary word or necessary preprositions.
            This is intended to help students fully understand the meaning of the sentence for use in vocabulary flashcards.
            ###Example###
            input: 
            Sentence: "IPräsident Emmanuel Macron hatte nach massiven Verlusten bei der Europawahl für den 30. Juni Neuwahlen zur Nationalversammlung angesetzt." 
            Word to preserve: "angesetzt"
            output: Präsident Macron <tag>hatte</tag> Neuwahlen <tag>angesetzt</tag>.
            ###Question###
            Sentence: {sentence} 
            Word to preserve: {word}
            """
        )
        self.simplifier = simplify_prompt | gpt4 | parser

        lookup_prompt = PromptTemplate.from_template(
            """
            ###Instruction###
            You are a German linguist, your task is to select the most accurate explanation for a word 
            within a given sentence from a list of explanations provided in a dictionary format.
            You MUST ensure that your answer is unbiased and does not rely on stereotypes.
            You have enough time to think carefully and make your choice.
            ###Example###
            input:
            Sentence: "Als sie die Augen wieder öffnete, war Tom verschwunden."
            Word: "öffnete"
            Dictionary Explanations:
            <dictionary>
            öffnen
            ọ̈ff|nen <sw. V.; hat> [mhd. offenen, ahd. offinōn, zu offen]:
            1.
            a) bewirken, dass etw. offen ist:
            b) jmdm., der Einlass begehrt, die [Haus- od. Wohnungs]tür aufschließen, aufmachen:
            c) mit der Geschäftszeit, den Dienststunden (2) beginnen; aufmachen:
            2. <ö. + sich>
            a) geöffnet werden:
            b) sich entfalten, sich auseinander falten:
            c) sich einem Menschen, einer Sache innerlich aufschließen; aufgeschlossen sein für jmdn., etw.:
            d) sich jmdm. erschließen, darbieten, auftun:
            </dictionary>
            output: bewirken, dass etw. offen ist
            ###Question###
            Sentence: {sentence}
            Word: {word}
            Dictionary: <dictionary>{dictionary}</dictionary>
            """
        )
        self.explanations_reducer = lookup_prompt | gpt4 | parser

        # initialize web summarzing model
        llm = ChatOpenAI(
            api_key=os.getenv("api_key"),
            base_url=os.getenv("base_url"),
            model="gpt-3.5-turbo-0125",
        )
        parser = StrOutputParser()
        summarize_prompt = PromptTemplate.from_template(
            """
            ###Instruction###
            Fassen Sie die wichtigsten Punkte und Hauptideen des bereitgestellten Webseiteninhalts zusammen. 
            Ihre Zusammenfassung muss prägnant und informativ sein, wobei die wesentlichen Informationen und Hauptthemen erfasst werden sollen. 
            Verwenden Sie die Originalsprache des Textes, aber vereinfachen Sie komplexe Wörter. 
            Achten Sie darauf, objektiv zu bleiben und vermeiden Sie unnötige Details. 
            Die Zusammenfassung sollte nicht mehr als 50 Wörter umfassen und logisch strukturiert sein.
            ###Kontext###
            <text>{context}<text>
            """
        )
        parser = StrOutputParser()
        self.summrizer = summarize_prompt | llm | parser
