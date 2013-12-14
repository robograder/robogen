import sqlite3
import sys
import csv
import itertools
from collections import namedtuple
import re

conn = sqlite3.connect('db/words.db')
c = conn.cursor()

# constants
VERB = 'verb'
NOUN = 'noun'
ADJ = 'adjective'
ADV = 'adverb'
CONNECTIVE = 'connective'

JUDGPOS = 1
JUDGNEG = -1
JUDGNONE = 0

# column name normalization
def get_col_name(w):
    return re.escape(w.split()[0].lower().strip())

# strip extra stuff off word 'names', like the [part of speech] disambiguator
def get_raw_word(w):
    return w.split('[')[0].strip()

# check csv integrity
def checkfile(fname = 'wordlist.csv'):
    with open(fname, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = reader.next()
        words = {}

        SimpleWord = namedtuple('SimpleWord', ['word'] + [get_col_name(col) for col in header[1:]])

        for row in reader:
            w = row[0]
            # no duplicate words
            if w in words:
                print 'Duplicate {}. Fix input data!'.format(row[0])

            wordinfo = SimpleWord(*[w] + [1 if i == 'x' else 0 for i in row[1:]])

            # check that it's only one part of speech
            if wordinfo.verb + wordinfo.noun + wordinfo.adjective + wordinfo.adverb + wordinfo.connective != 1:
                print '{} must have a single part of speech.'.format(w)

            # check sub-criteria
            if (wordinfo.transitive or wordinfo.intransitive) and not wordinfo.verb:
                print '{} is transitive or intransitive but not a verb.'.format(w)
            if wordinfo.countable and not wordinfo.noun:
                print '{} is countable but not a noun.'.format(w)
            if (wordinfo.positive or wordinfo.negative) and not wordinfo.judgmental:
                print '{} is positive or negative but not judgmental.'.format(w)
            # is this really a sub-criterion??
            if wordinfo.hedge and not wordinfo.adverb:
                print '{} is hedge but not an adverb.'.format(w)

            # for verbs...
            if wordinfo.verb:
                # check that it's exactly one of these two
                if wordinfo.transitive == wordinfo.intransitive:
                    print 'Verb {} can\'t be both transitive and intransitive.'.format(w)

            # for judgments...
            if wordinfo.judgmental:
                if wordinfo.positive + wordinfo.negative == 2:
                    print 'Judgmental word {} can\'t be both positive and negative.'.format(w)

            words[w] = wordinfo

# import words into db
def importwordsdb(fname = 'wordlist.csv', table = 'words'):
    with open(fname, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = reader.next()

        # simple word wrapper class
        SimpleWord = namedtuple('SimpleWord', ['word'] + [get_col_name(col) for col in header[1:]])

        c.execute('''drop table {}'''.format(table))
        # ... if not exists [ no longer needed ]
        c.execute('''create table {} (word varchar(25), partofspeech varchar(15), transitive boolean, countable boolean, hedge boolean, judgmental integer);'''.format(
            table) )

        print c.execute('pragma table_info({});'.format(table)).fetchall()

        n = 0
        for row in reader:
            n += 1

            wordinfo = SimpleWord(*[row[0]] + [1 if i == 'x' else 0 for i in row[1:]])
            
            # populate stuff to put into the row
            dbrowdict = {}

            if wordinfo.verb:
                dbrowdict['partofspeech'] = VERB
            elif wordinfo.noun:
                dbrowdict['partofspeech'] = NOUN
            elif wordinfo.adjective:
                dbrowdict['partofspeech'] = ADJ
            elif wordinfo.adverb:
                dbrowdict['partofspeech'] = ADV
            elif wordinfo.connective:
                dbrowdict['partofspeech'] = CONNECTIVE

            if wordinfo.positive:
                dbrowdict['judgmental'] = JUDGPOS
            elif wordinfo.negative:
                dbrowdict['judgmental'] = JUDGNEG
            else: # not judgmental
                dbrowdict['judgmental'] = JUDGNONE

            dbrowdict['countable'] = wordinfo.countable
            dbrowdict['hedge'] = wordinfo.hedge
            dbrowdict['transitive'] = wordinfo.transitive

            rowkeys = dbrowdict.keys()
            rowvals = [dbrowdict[i] for i in rowkeys]

            c.execute('''insert into {} {!s} values {!s};'''.format(
                table, tuple(['word'] + rowkeys), tuple([row[0]] + rowvals) ) )

        conn.commit()
        print '{!s} rows inserted into table {}'.format(n, table)

# import words into db, old schema
def importwordsdb_old(fname = 'wordlist.csv', table = 'words'):
    with open(fname, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = reader.next()
        cols = [get_col_name(header[0]) + ' varchar(25)'] + [get_col_name(s) + ' boolean' for s in header[1:]]
        c.execute('''create table if not exists {} ({!s});'''.format(
            table, ', '.join(cols) ) 
            )

        print c.execute('pragma table_info({});'.format(table)).fetchall()

        n = 0
        for row in reader:
            n += 1
            values = [row[0].lower()] + [1 if s.lower() == 'x' else 0 for s in row[1:]]

            c.execute('''insert into {} values {!s};'''.format(
                table, tuple(values) ) )

        conn.commit()
        print '{!s} rows inserted into table {}'.format(n, table)

def print_usage():
    print '''Usage:
    wordimport.py <name of csv to import> <name of database table>
    
    or 
    
    wordimport.py <name of csv to check>'''

def main():
    if len(sys.argv) == 3:
        importwordsdb(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        checkfile(sys.argv[1])
    else:
        print_usage()
        return

if __name__ == '__main__':
    main()

