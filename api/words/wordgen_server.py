import wordimport as wi
from collections import namedtuple
import random
import json

import bottle
from bottle import request, template, response
from bottle.ext import sqlite

app = bottle.Bottle()
plugin = sqlite.Plugin(dbfile='db/words.db')
app.install(plugin)

#WordDBRow = namedtuple('WordDBRow', ['word', 'partofspeech', 'transitive', 'countable', 'hedge', 'judgmental'])

@app.get('/words')
def request_words():
    return template('words')

@app.post('/words')
def find_words_html(db):
    return template('wordresult', wordlist=find_words(db))

@app.post('/words.json')
def find_words_json(db):
    response.content_type = 'application/json'
    return {'words': find_words(db)}

@app.post('/words_dada.json')
def find_words_dada_json(db):
    response.content_type = 'application/json'
    return {'words': find_words(db)}

def find_words(db):
    partofspeech = request.forms.get('partofspeech')
    transitive = 1 if request.forms.get('transitive') else 0
    countable = 1 if request.forms.get('countable') else 0
    hedge = 1 if request.forms.get('hedge') else 0
    judgmental = int(request.forms.get('judgmental'))
    count = int(request.forms.get('count'))

    print [partofspeech, transitive, countable, hedge, judgmental, count]

    if partofspeech == wi.VERB:
        result = db.execute('''select word from words where partofspeech="verb" and transitive=? and judgmental=?;''', (transitive,judgmental)).fetchall()
    elif partofspeech == wi.NOUN:
        result = db.execute('''select word from words where partofspeech="noun" and countable=? and judgmental=?;''', (countable,judgmental)).fetchall()
    elif partofspeech == wi.ADJ:
        result = db.execute('''select word from words where partofspeech="adjective" and judgmental=?;''', (judgmental,)).fetchall()
    elif partofspeech == wi.ADV:
        result = db.execute('''select word from words where partofspeech="adverb" and hedge=? and judgmental=?;''', (hedge, judgmental)).fetchall()
    elif partofspeech == wi.CONNECTIVE:
        result = db.execute('''select word from words where partofspeech="connective";''').fetchall()
    else:
        return
        #raise ValueError('Bad part of speech!')

    result = [wi.get_raw_word(str(i[0])) for i in result]
    return random.sample(result, min(len(result), int(count)))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
