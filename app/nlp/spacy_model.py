import spacy


class SpacyModel:
    """
    This class has benn deprecated
    """

    def __init__(self) -> None:
        self.segmenter = spacy.load("de_core_news_md")

        self.lemmatizer = spacy.blank("de")
        self.lemmatizer.add_pipe("lemmatizer", config={"mode": "lookup"})
        self.lemmatizer.initialize()

    def segment(self, text: str, pos_start: int):
        doc = self.segmenter(text)
        for sent in doc.sents:
            if sent.end_char > pos_start:
                return sent.text

    def lemmatize(self, word):
        lemmas = self.lemmatizer(word)
        # actually there should be only one
        for lemma in lemmas:
            return lemma.lemma_

    def lemmtatize_rule(self, word):
        # lemmatizer = self.segmenter.get_pipe("lemmatizer")
        # print(lemmatizer.mode)
        for token in self.segmenter(word):
            return token.lemma_
