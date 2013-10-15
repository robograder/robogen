from bs4 import BeautifulSoup as bsoup
import urllib2
import re
import random
import subprocess

sentenceEnd = re.compile(r'([\.!?]+ )')

# split line into sentences
def splitSentences(essay):
    return [endSentence(s) for s in re.sub(sentenceEnd, '\g<1>|||', essay).split('|||')]

def endSentence(sentence):
    sentence = sentence.strip()
    if len(sentence) < 1:
        return sentence
    if sentence[-1] not in ('.', '!', '?'):
        sentence += '.'
    return sentence

class EssayGenerator:
    """abstract base class for different generators.

    An 'essay' is a list of sentences (ending in periods, for simplicity).
    
    generateEssay() should generate a new essay.
    getSentence() should get a (usually) new sentence from the current essay.
    getRandomSentence() should get a random sentence from the current essay.
    """
    def __init__(self):
        self.essay = []
        self.sentenceIndex = 0
        pass

    def generateEssay(self):
        self.sentenceIndex = 0
        self.essay = []
    
    def __iter__(self):
        return self

    def next(self):
        return self.getSentence()

    def __next__(self):
        return self.getSentence()

    def getSentence(self):
        l = len(self.essay)
        if l == 0:
            self.sentenceIndex = 0
            raise StopIteration()
        else:
            s = self.essay[self.sentenceIndex]
            self.sentenceIndex = (self.sentenceIndex+1)%l
            return s

    def getRandomSentence(self):
        return self.essay[random.randint(0, len(self.essay)-1)]

class PostmodernGenerator(EssayGenerator):
    def generateEssay(self):
        self.sentenceIndex = 0
        self.essay = _getPostmodernSentences()

newline = re.compile(r'\n')
cite = re.compile(r'\[[0-9]+\]')

def _getPostmodernSentences(url = 'http://dev.null.org/postmodern/'):
    soup = bsoup(urllib2.urlopen(url, 'html5lib').read())
    sentences = []

    for tag in soup.body.children: # read all <p> tags up to the first <hr>
        if tag.name == 'p':
            sentences.extend([_parsePostmodern(s) for s in splitSentences(tag.get_text()) if len(s) > 1])
        if tag.name == 'hr':
            break

    return sentences

def _parsePostmodern(sentence):
    return re.sub(cite, '', re.sub(newline, '', sentence)) 

# matches \begin{...}, \end{...}
env = re.compile(r'\\(begin|end)\{.+\}')
# matches \textbf{...}
bold = re.compile(r'\\textbf\{(.+)\}')
# matches \cite{...}
citation = re.compile(r'\\cite\{(.+)\}')
# matches $...$
inlinemathmode = re.compile(r'\$(.+)\$')
# matches \[...\]
displaymathmode = re.compile(r'\\\[(.+)\\\]')
# matches \asdf[_^]{...}[_^]{...}...
command = re.compile(r'\\[a-zA-Z]+([_\^]?\{.*\})')    
# matches \asdf that is not followed by _, ^, {
symbol = re.compile(r'\\([a-zA-Z])+[^_\^\{]')    
# matches stray \, {, }
specialchars = re.compile(r'[\\\{\}]')

# tmp path for tex file
__tmp_path = '../generated/TEMP_MATH.tex'

def _parseLatexDumb(sentence):
    if re.search(env, sentence) or re.search(inlinemathmode, sentence) or re.search(displaymathmode, sentence):
        return ''

    return re.sub(specialchars, '', 
        re.sub(symbol, '\g<1>', 
            re.sub(command, '', # kill commands
                re.sub(bold, '\g<1>', # replace bold with contents
                    re.sub(citation, 'citation', sentence)
                )
            )
        )
    )

def _parseFile(fname, parser=_parseLatexDumb):
    sentences = []
    with open(fname, 'r') as f:
    # assume each line is a paragraph or a command (i.e. no sentences span multiple lines)
        for l in f:
            sentences.extend([parser(s) for s in splitSentences(l)])

    return [s for s in sentences if len(s) > 1] # assume a sentence > 3char

class MathGen(EssayGenerator):
    def generateEssay(self):
        self.sentenceIndex = 0

        subprocess.call('../mathgen/mathgen.pl', '--mode=raw', '--output=' + __tmp_path)
        self.essay = _parseFile(__tmp_path)

