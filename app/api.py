from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .nlp import load
from .type import *
import sqlite3
import json
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "card.db")
app = FastAPI()
lp = LanguageProcessor()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
def query_freq(word:str) -> int:
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute('select * from De_frequency WHERE lemma=?;', (word,))
        value = cursor.fetchall()
    if len(value) != 1:
        return -1
    else:
        lemma, hits, freq = value[0]
        # print(f"{lemma}: {hits} | {freq}")
        return freq

def parse_data_from_db(keys, raw_data):
    list_of_dict = [
        dict(zip(keys, values))
        for values in raw_data
    ]
    return list_of_dict

@app.get("/cards")
async def get_cards(user_id: int) -> dict:
    def get_cards_from_db(user_id: int) -> any:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.cursor()
            cursor.execute('SELECT * FROM cards WHERE user_id = ?', (user_id,))
            value = cursor.fetchall()
            return value
    keys = ('id', 'user_id', 'lang','selected_word', 'context' , 'url', 'date', 'pos_start', 'pos_end', 'sentence', 'lemma', 'frequency', 'summary')
    cards = parse_data_from_db(keys, get_cards_from_db(user_id))
    interested_fields = ['id', 'lang', 'selected_word', 'context', 'url', 'date', 'sentence', 'lemma', 'frequency', 'summary']
    filtered = [ { x: card[x] for x in interested_fields} for card in cards]
    return {"cards": filtered}

@app.post("/cards/")
async def add_card(item: BrowserSelection, user_id: int) -> dict:
    # trim whitespace
    word = item.text[item.start:item.end]
    word = word.strip()
    print(f"select word: {word}")
    sentence = lp.segment(item.text, item.start)
    page = lp.page_summarize(item.url)
    # not lemmatize multiple words
    lemma = None if (len(word.split(" ")) > 1) else lp.lemmatize(word) 
    frequency = -1 if lemma is None else query_freq(lemma)

    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        insert_sql_template = 'INSERT INTO cards\
        (user_id, lang, selected_word, context , url, pos_start, pos_end, lemma, sentence, frequency, page_summary)\
        VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
        params = (user_id, item.lang, word, item.text, item.url, item.start, item.end, lemma, sentence, frequency, page)
        cursor.execute(insert_sql_template, params)
        db.commit()
    return {
        "message":  "card added." 
    }

@app.delete("/cards/{card_id}")
async def delete_card(card_id: int):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.cursor()
            delete_sql_template = 'DELETE FROM cards WHERE id = ? ;'
            params = (card_id,)
            cursor.execute(delete_sql_template, params)
            db.commit()
    except Exception as e:
        print(e)
        return{"error": "fail to open databse"}
    return {
        "message":  "card deleted.", 
        "ID": card_id
    }

@app.get("/mappings/")
async def get_mappings(user_id: int):
    def get_mappings_from_db(user_id: int) -> any:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.cursor()
            cursor.execute('SELECT * FROM mappings WHERE user_id = ?', (user_id,))
            value = cursor.fetchall()
            return value
    keys = ('id', 'user_id', 'lang', 'template_id', 'template_name', 'fields')
    mappings = parse_data_from_db(keys, get_mappings_from_db(user_id))
    for mapping in mappings:
        mapping['fields'] = json.loads(mapping['fields'])
    return mappings

@app.post("/mappings/")
async def add_mappings(data: BaseMapping, user_id:int):
    dict_data = data.model_dump()
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.cursor()
            insert_sql_template = 'INSERT INTO mappings\
            (user_id, lang, template_id, template_name, fields)\
            VALUES( ?, ?, ?, ?, ?);'
            params = (user_id, 
                      dict_data['lang'], 
                      dict_data['template_id'], 
                      dict_data['template_name'], 
                      json.dumps(dict_data['fields']))
            cursor.execute(insert_sql_template, params)
            db.commit()
    except Exception as e:
        print(e)
        return{"error": "fail to open databse"}