import re

# enum for parser state
class ParseState:
    TEXT = 1
    MATH = 2
    COMMMAND = 3

    match = { '{': '}', '$': '$', '\[': '\]' }

def parseSentence(sentence):
    curtoken = ''
    state = ParseState.TEXT
    for i in xrange(len(line)):
        if state == ParseState.MATH:
            pass
        # kill things between $...$, \[...\]
        

# matches \begin{...}, \end{...}
env = re.compile(r'\\(begin|end)\{.+\}')

# matches \textbf{...}
bold = re.compile(r'\\textbf\{(.+)\}')

# matches \textbf{...}
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

def dumbParseSentence(sentence):
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

def endSentence(sentence):
    sentence = sentence.strip()
    if sentence[-1] not in ('.', '!', '?'):
        sentence += '.'
    return sentence

def parseFile(fname, parser=dumbParseSentence):
    sentences = []
    with open(fname, 'r') as f:
    # assume each line is a paragraph or a command (i.e. no sentences span multiple lines)
        for l in f:
            sentences.extend([parser(s) for s in l.split('. ')])

    return [endSentence(s) for s in sentences if len(s) > 10]

