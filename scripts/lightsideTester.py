import requests
import json
import generateEssay as ge
from bs4 import BeautifulSoup as bsoup

AUTH_TOKEN = '89afd360213fa97babfbd7775a8cbf9c38f0fe1d'
ROOT_URL = "https://try-api.lightsidelabs.com/api/"
headers = {"Authorization": "Token " + AUTH_TOKEN, "Content-Type": "application/json"}

# Helpers
def getIdFromResponse(response): # for use with responses containing a 'url' which is a RESTful route with integer id
    url = json.loads(response.content)['url']
    return int(url.split('/')[-1])

def multidictPut(d, k, v): # put things into multi-valued dictionary 
    if k in d:
        d[k].append(v)
    else:
        d[k] = [v]

def getCorpusURL(corpus_id):
    return ROOT_URL + 'corpora/' + str(corpus_id)

def getTrainingAnswerURL(answerId):
    return ROOT_URL + 'training-answers/' + str(answerId)

def checkStatus(response, successCodes, errorText):
    if response.status_code not in successCodes:
        raise requests.exceptions.RequestException("Code " + str(response.status_code) + ": " + errorText + '\n' + response.content)

class LightsideTester:
    ''' Wrappers for the Lightside API, for use with a single corpus of a single prompt at a time. '''

    def __init__(self, author_id=None, authToken = AUTH_TOKEN):
        self.authToken = authToken
        self.headers = {"Authorization": "Token " + AUTH_TOKEN, "Content-Type": "application/json"}
        self.trainingAnswerMap = {} # maps essay id to training answer id
        self.trainingScoresMap = {} # maps essay id to ids of human scores
        self.answerMap = {} # maps generated essay id to answer id
        self.corpus_id = None

        if(author_id == None):
            self.newAuthor()
        else:
            self.setAuthor(author_id)

    # Author stuff
    def newAuthor(self):
        username = raw_input("Author username? ")
        email = raw_input("Author email? ")
        data = {"designator": username, "email": email}
        r = requests.post(ROOT_URL + "authors/", data=json.dumps(data), headers=self.headers)
        self.author_id = getIdFromResponse(r)

    def setAuthor(self, author_id):
        r = requests.get(ROOT_URL + "authors/" + str(author_id), headers=self.headers)
        if r.status_code != 200: # if failure
            print 'Author id not found on remote server.'
            self.newAuthor()
        else:
            self.author_id = getIdFromResponse(r)

    # Corpus stuff
    def newCorpus(self, prompt_id):
        description = raw_input("Description of corpus? ")
        data = {"prompt": ROOT_URL + "prompts/" + str(prompt_id), "description": description}
        r = requests.post(ROOT_URL + "corpora/", data=json.dumps(data), headers=self.headers)
        checkStatus(r, [201], "Prompt id not found on remote server, or description was illegal.")

        self.prompt_id = prompt_id
        self.corpus_id = getIdFromResponse(r)

    def setCorpus(self, corpus_id):
        r = requests.get(getCorpusURL(corpus_id), data=json.dumps(data), headers=self.headers)
        checkStatus(r, [200], "Corpus id not found on remote server.")

        self.corpus_id = corpus_id

    # Training answers and scores
    def addTrainingAnswer(self, essay):
        data = {"corpus": getCorpusURL(self.corpus_id), "text": essay.getText()}
        r = requests.post(ROOT_URL + "training-answers/", data=json.dumps(data), headers=self.headers)
        self.trainingAnswerMap[essay.essay_id] = getIdFromResponse(r)

    def addTrainingScore(self, essay, scoreName='domain1_score'):
        if essay.essay_id not in self.trainingAnswerMap:
            raise LookupError("Essay hasn't been added to training answers yet.")
            return

        data = { "training_answer": getTrainingAnswerURL(self.trainingAnswerMap[essay.essay_id]),
                 "label": str(essay.getScore(scoreName)) }
        r = requests.post(ROOT_URL + "human-scores/", data=json.dumps(data), headers=self.headers)
        self.trainingScoresMap[essay.essay_id] = getIdFromResponse(r)

    def addBulkTrainingAnswers(self, prompt_id, fname='../data/prompt2_lightside.csv'):
        if self.corpus_id == None:
            self.newCorpus(prompt_id)

        r = requests.get(ROOT_URL + 'corpus-upload-parameters/', headers=self.headers)

        checkStatus(r, [200], "Request to get corpus upload parameters failed.")

        params = json.loads(r.content)
        data2 = { 'AWSAccessKeyId': params['access_key_id'], 'key': params['key'], 'acl': 'public-read',
                'Policy': params['policy'], 'Signature': params['signature'], 'success_action_status': '201' }
        files2 = {'file': open(fname, 'rb')}
        r2 = requests.post(params['s3_endpoint'], data=data2, files=files2)

        checkStatus(r2, [201], "Request to S3 failed.")

        soup = bsoup(r2.content)
        key = soup.find('Key').get_text()

        data3 = {'corpus': getCorpusURL(self.corpus_id), 's3_key': key, 'content_type': 'text/csv'}

        r3 = requests.post(ROOT_URL + "corpus-upload-tasks/", data=data3, headers=self.headers)
        r4 = requests.post(ROOT_URL + "corpus-upload-tasks/" + str(getIdFromResponse(r3)) + '/process', headers=headers)

        checkStatus(r4, [200, 202], "Queueing of corpus upload task failed.")



    #def addNewAnswer(self, essay):

