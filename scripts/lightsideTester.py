import sys
import time

import requests
import json
from bs4 import BeautifulSoup as bsoup

import essay
import generateEssay as ge
import lightsideRestHelpers as lsrh

AUTH_TOKEN = '89afd360213fa97babfbd7775a8cbf9c38f0fe1d'
headers = {"Authorization": "Token " + AUTH_TOKEN, "Content-Type": "application/json"}

# Helpers

class LightsideTester:
    ''' Wrappers for the Lightside API, for use with a single corpus of a single prompt at a time. '''

    def __init__(self, author_id=None, authToken = AUTH_TOKEN):
        self.authToken = authToken
        self.headers = {"Authorization": "Token " + AUTH_TOKEN, "Content-Type": "application/json"}
        self.trainingAnswerMap = {} # maps essay id to training answer id
        self.trainingScoresMap = {} # maps essay id to ids of human scores
        self.answerMap = {} # maps generated essay id to answer id
        self.corpus_id = None
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.answer_set_id = None

        if(author_id == None):
            self.newAuthor()
        else:
            self.setAuthor(author_id)

    # Author stuff
    def newAuthor(self):
        username = raw_input("Author username? ")
        email = raw_input("Author email? ")
        data = {"designator": username, "email": email}
        r = self.session.post(lsrh.getAuthorURL(), data=json.dumps(data))
        self.author_id = lsrh.getIdFromResponse(r)
        print 'Set author to', self.author_id

    def setAuthor(self, author_id):
        r = self.session.get(lsrh.getAuthorURL(author_id), headers=self.headers)
        if r.status_code != 200: # if failure
            print 'Author id not found on remote server.'
            self.newAuthor()
        else:
            self.author_id = lsrh.getIdFromResponse(r)
            print 'Set author to', self.author_id

    # Prompts
    # note: prompt 6 is the robograder copy of "prompt 2"
    def getPrompt(self, prompt_id):
        r = self.session.get(lsrh.getPromptURL(prompt_id))
        lsrh.checkStatus(r, (201,), "Prompt id not found on remote server")

        return r

    # Corpus stuff
    def newCorpus(self, prompt_id):
        description = raw_input("Description of corpus? ")
        data = {"prompt": lsrh.getPromptURL(prompt_id), "description": description}
        r = self.session.post(lsrh.getCorpusURL(), data=json.dumps(data), headers=self.headers)
        lsrh.checkStatus(r, (201,), "Prompt id not found on remote server, or description was illegal.")

        self.prompt_id = prompt_id
        self.corpus_id = lsrh.getIdFromResponse(r)

        print 'New corpus with id {} for prompt {}'.format(self.corpus_id, self.prompt_id)

    def setCorpus(self, corpus_id):
        r = self.session.get(lsrh.getCorpusURL(corpus_id))
        lsrh.checkStatus(r, (200,), "Corpus id not found on remote server.")

        response = r.json()

        self.prompt_id = lsrh.getIdFromURL(response["prompt"])
        self.corpus_id = corpus_id
        print 'Set corpus to id {} for prompt {}'.format(self.corpus_id, self.prompt_id)

    # Training answers and scores
    def addTrainingAnswer(self, essay):
        data = {"corpus": lsrh.getCorpusURL(self.corpus_id), "text": essay.getText()}
        r = self.session.post(lsrh.getTrainingAnswerURL(), data=json.dumps(data))
        self.trainingAnswerMap[essay.essay_id] = lsrh.getIdFromResponse(r)

    def addTrainingScore(self, essay, scoreName='domain1_score'):
        if essay.essay_id not in self.trainingAnswerMap:
            raise LookupError("Essay hasn't been added to training answers yet.")
            return

        data = { "training_answer": lsrh.getTrainingAnswerURL(self.trainingAnswerMap[essay.essay_id]),
                 "label": str(essay.getScore(scoreName)) }
        r = self.session.post(lsrh.getHumanScoreURL(), data=json.dumps(data), headers=self.headers)
        self.trainingScoresMap[essay.essay_id] = lsrh.getIdFromResponse(r)

    # Answers and answer sets
    def addAnswer(self, text):
        data = { "author": lsrh.getAuthorURL(self.author_id),
                 "prompt": lsrh.getPromptURL(self.prompt_id),
                 "text": text }

        r = self.session.post(lsrh.getAnswerURL(), data=json.dumps(data))
        lsrh.checkStatus(r, (201,), "Failed to upload answer.")

    def addAnswerSet(self, trained_models = [], tags = []):
        data = { "prompt": lsrh.getPromptURL(self.prompt_id),
                 "trained_models": [lsrh.getTrainedModelURL(t) for t in trained_models] if len(trained_models) > 0 else [], 
                 "tags": tags }

        r = self.session.post(lsrh.getAnswerSetURL(), data=json.dumps(data))
        lsrh.checkStatus(r, (201,), "Failed to create answer set.")

        self.answer_set_id = lsrh.getIdFromResponse(r)

    def setAnswerSet(self, answer_set_id):
        r = self.session.get(lsrh.getAnswerSetURL(answer_set_id))
        try:
            lsrh.checkStatus(r, (200,), "Answer set doesn't exist")
        except:
            return

        self.answer_set_id = answer_set_id


    # Tasks: bulk uploading of training answers/answers, training the model
    def uploadToS3(self, uploadType, fname):
        ''' Upload file to S3 and return the response. '''
        # get upload params
        if uploadType == "corpus":
            r = self.session.get(lsrh.getCorpusUploadParametersURL())
        elif uploadType == "answerset":
            r = self.session.get(lsrh.getAnswerSetUploadParametersURL())
        else:
            raise ValueError("Must upload either a corpus or answerset to s3")

        lsrh.checkStatus(r, (200,), "Request to get {} upload parameters failed.".format(uploadType))

        params = r.json()
        data2 = { 'AWSAccessKeyId': params['access_key_id'], 'key': params['key'], 'acl': 'public-read',
                'Policy': params['policy'], 'Signature': params['signature'], 'success_action_status': '201' }

        with open(fname, 'rb') as uploadfile:
            files2 = {'file': uploadfile}
            # upload to s3
            r2 = requests.post(params['s3_endpoint'], data=data2, files=files2)
            lsrh.checkStatus(r2, (201,), "Request to S3 failed.")

            return r2

    def waitForTask(self, url, taskName, interval=20):
        ''' Block until task finishes; check every [interval] seconds.
            Return request response. '''
        while True:
            time.sleep(interval)
            r = self.session.get(url)
            lsrh.checkStatus(r, (200,), "Couldn't access {}...".format(taskName))
            uploadStatus = r.json()["status"]
            # MAGIC VALUES: Lightside API uses 'S' for success, 'F' for failure, 'W' for "task hasn't yet been submitted"; everything else is queueing/waiting
            if uploadStatus == 'S':
                print ''
                return r
            elif uploadStatus == 'F' or uploadStatus == 'U':
                raise ValueError("{} failed!".format(taskName.capitalize()))
            elif uploadStatus == 'W':
                raise ValueError("{} hasn't been submitted for processing!".format(taskName.capitalize()))
            else:
                print '.',
                sys.stdout.flush()

    def uploadCorpus(self, prompt_id, fname):
        ''' Create a new corpus of training answers, given the prompt_id and a file containing
            the corpus. '''
        self.newCorpus(prompt_id)

        r = self.uploadToS3('corpus', fname)

        soup = bsoup(r.content)
        key = soup.find('key').get_text()

        data2 = {'corpus': lsrh.getCorpusURL(self.corpus_id), 's3_key': key, 'content_type': 'text/csv'}

        # create and start upload task
        r2 = self.session.post(lsrh.getCorpusUploadTaskURL(), data=json.dumps(data2))
        corpusUploadTaskData = r2.json()
        r3 = self.session.post(corpusUploadTaskData["process"])

        lsrh.checkStatus(r3, (200, 202), "Queueing of corpus upload task failed.")

        r4 = self.waitForTask(corpusUploadTaskData["url"], "corpus upload task")
        return r3.json()["corpus"]

    def trainModel(self):
        ''' Train model based on the training answers for the current corpus.
            Returns url of trained_model. '''
        # create and start training task
        data = {"corpus": lsrh.getCorpusURL(self.corpus_id)}
        r = self.session.post(lsrh.getTrainingTaskURL(), data=json.dumps(data))
        lsrh.checkStatus(r, (201,), "Failed to create training task")

        trainingTaskData = r.json()
        r2 = self.session.post(trainingTaskData["process"])

        r3 = self.waitForTask(trainingTaskData["url"], "training task")

        return r3.json()["trained_model"]

    def uploadAnswerSet(self, fname):
        if self.answer_set_id == None:
            self.addAnswerSet()

        r = self.uploadToS3('answerset', fname)

        soup = bsoup(r.content)
        key = soup.find('key').get_text()

        data2 = {'prompt': lsrh.getPromptURL(self.prompt_id), 'answer_set': lsrh.getAnswerSetURL(self.answer_set_id), 's3_key': key, 'content_type': 'text/csv'}

        # create and start upload task
        r2 = self.session.post(lsrh.getAnswerSetUploadTaskURL(), data=json.dumps(data2))
        answerUploadTaskData = r2.json()
        r3 = self.session.post(answerUploadTaskData["process"])

        lsrh.checkStatus(r3, (200, 202), "Queueing of answerset upload task failed.")

        r4 = self.waitForTask(answerUploadTaskData["url"], "answer set upload task")
        return r4.json()["answer_set"]

    def runPredictions(self):
        ''' Returns list of urls of prediction results. '''
        data = { "answer_set": lsrh.getAnswerSetURL(self.answer_set_id) }
        r = self.session.post(lsrh.getPredictionTaskURL(), data=json.dumps(data))

        lsrh.checkStatus(r, (201,), "Failed to create prediction task")

        predictionTaskData = r.json()
        r2 = self.session.post(predictionTaskData["process"])

        r3 = self.waitForTask(predictionTaskData["url"], "prediction task")

        return r3.json()["prediction_results"]

    def getPredictionResults(self, resulturls):
        # get actual result json objects
        results = [self.session.get(url).json() for url in resulturls]
        # text from associated answer. score is the label with the highest coefficient.
        texts_and_scores = [ (self.session.get(a['answer']).json()['text'], max(a['label'].items(), lambda i: i[1])[0] ) for a in results ]
        return texts_and_scores

    #def addNewAnswer(self, essay):

