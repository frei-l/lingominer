import chromadb
import os
import uuid

from lingominer.global_env import CHROMA_DIR
from lingominer.context import user_id_var
from lingominer.models import Card
import chromadb.utils.embedding_functions as embedding_functions

client = chromadb.PersistentClient(path=CHROMA_DIR.as_posix())
ef = embedding_functions.OpenAIEmbeddingFunction(
    api_base=os.environ["OPENAI_PROXY"],
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small",
)


card_field_id = {"word": 0}


def get_collection_name():
    return f"{user_id_var.get()}"


def upsert_card(card: Card):
    collection = client.get_or_create_collection(
        get_collection_name(), embedding_function=ef
    )
    collection.add(
        documents=[card.word],
        metadatas=[{"id": str(card.id), "lang": card.lang, "field": "word"}],
        ids=[f"{str(card.id)}_{card_field_id['word']}"],
    )


def search_cards(query: str):
    collection = client.get_collection(get_collection_name(), embedding_function=ef)
    return collection.query(query_texts=[query], n_results=10)


def delete_card(card_id: uuid.UUID):
    collection = client.get_collection(get_collection_name(), embedding_function=ef)
    collection.delete(where={"id": str(card_id)})


def upsert_card_test(word: list[str]):
    try:
        client.delete_collection("test_collection")
    except Exception as e:
        pass
    collection = client.get_or_create_collection(
        "test_collection", embedding_function=ef
    )
    collection.add(
        documents=word,
        metadatas=[{"id": i}for i in range(len(word))],
        ids=[str(i) for i in range(len(word))],
    )


def search_cards_test(query: str):
    collection = client.get_collection("test_collection", embedding_function=ef)
    return collection.query(query_texts=[query], n_results=3)


if __name__ == "__main__":
    upsert_card_test(
        [
            "hello",
            "world",
            "food",
            "love",
            "life",
            "time",
            "work",
            "money",
            "health",
            "happiness",
        ]
    )
    result = search_cards_test("Zeit")
    cards = []
    for i in result["metadatas"][0]:
        cards.append(i["id"])
    print(cards)