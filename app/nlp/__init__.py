from .nlp import German, BaseLanguage

def load(language: str) -> BaseLanguage:
    supported_languages = {
        'de': German
    }
    try:
        return supported_languages[language]()
    except KeyError:
        raise ValueError(f"Unsupported language: {language}")