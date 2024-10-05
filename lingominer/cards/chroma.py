import chromadb

from lingominer.global_env import CHROMA_DIR
from lingominer.core.context_var import user_id
from lingominer.schemas import Card
client = chromadb.PersistentClient(path=CHROMA_DIR.as_posix())

def get_collection_name():
    return f"{user_id.get()}"


def upsert_card(card: Card):
    collection = client.get_or_create_collection(get_collection_name())
    collection.add(
        documents=[card.word],
        metadatas=[{"id": card.id, "lang": card.lang, "field": "word"}],
    )

def search_cards(query: str):
    collection = client.get_collection(get_collection_name())
    return collection.query(query_texts=[query], n_results=10)

def upsert_card_test(word: list[str]):
    collection = client.get_collection("test_collection")
    collection.add(
        documents=word,
        ids=list(range(len(word))),
    )


if __name__ == "__main__":
    pass
