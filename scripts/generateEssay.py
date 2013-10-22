import parseGenerated as pg
import essay as ess
import csv
import cPickle as pickle

GENERATOR_OFFSET = 10**6
generators = {1: pg.PostmodernGenerator(), 2: pg.MathGen() }
essays = {}
generatedEssays = {}
header = []
DATA_PATH = '../data/'

def importEssays(fname='../data/training_set_rel3.csv', delim='|', prompt_id=None):
    """ fname: file name, delim: delimiter, prompt_id: integer id of prompt """
    global essays
    global header
    essays = {}
    header = []
    with open(fname, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=delim)
        header = reader.next()
        for row in reader:
            if prompt_id == None or str(prompt_id) == row[1]:
                # essay data
                essay_ = ess.Essay(int(row[0]), int(row[1]), row[2])
                # scores
                for i in xrange(3, len(row)):
                    if len(row[i]) > 0:
                        essay_.assignScore(header[i], int(row[i]))

                essays[essay_.essay_id] = essay_

    print len(essays), 'essays loaded'

def saveEssaysAsCsv(fname='training.csv'):
    with open(DATA_PATH+fname, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for ess_id in sorted(essays):
            ess = essays[ess_id]
            writer.writerow([ess.essay_id, ess.prompt_id, ess.text] + [ess.getScore(header[i]) for i in range(3, len(header))])

def dumpEssays(fname='essays.pickle'):
    pickle.dump((essays, generatedEssays), open(DATA_PATH+fname, 'w'))

def recoverEssays(fname='essays.pickle'):
    essays, generatedEssays = pickle.load(open(DATA_PATH+fname, 'r'))

def interleave1(essayText, generator):
    generator.generateEssay()
    # interleave and flatten
    return ' '.join([a for pair in zip(pg.splitSentences(essayText), generator) for a in pair])
    
def interleave1All(generator_id):
    global generatedEssays, essays
    generatedEssays = {}
    generator = generators[generator_id]
    count = 0
    for i in essays:
        if essays[i].getScore('domain1_score') == 4:
            if count % 10 == 0:
                print count
            count += 1
            generatedEssays[i] = ess.GeneratedEssay(generator_id*GENERATOR_OFFSET + i, essays[i].prompt_id, interleave1(essays[i].text, generator), i, generator_id)

def rpp2():
    runPostmodernPrompt2()

def runPostmodernPrompt2():
    print 'Importing prompt_id = 2 essays...'
    importEssays(prompt_id=2)
    print 'Interleaving with generator 1...'
    interleave1All(1)
    print 'Dumping essays and generated essays to file...'
    dumpEssays()
