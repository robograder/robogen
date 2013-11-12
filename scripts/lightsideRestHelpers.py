import requests
import json

''' Lightside REST API helper functions '''

ROOT_URL = "https://try-api.lightsidelabs.com/api/"

# General-purpose stuff
'''
def multidictPut(d, k, v): # put things into multi-valued dictionary 
    if k in d:
        d[k].append(v)
    else:
        d[k] = [v]
'''

# URL helpers
def getIdFromResponse(response): # for use with responses containing a 'url' which is a RESTful route with integer id
    return getIdFromURL(response.json()['url'])

def getIdFromURL(url):
    return int(url.split('/')[-1])

def addRootURL(url):
    return ROOT_URL + url

def addEndingSlash(url):
    return url if url[-1] == '/' else url + '/'

def makeRoute(routeName, resourceId=None, suffix=''):
    return addEndingSlash(addRootURL('/'.join((routeName, suffix)))) if resourceId == None else addEndingSlash(addRootURL('/'.join((routeName, str(resourceId), suffix))))

# Resources
def getAuthorURL(author_id=None):
    return makeRoute('authors', author_id)

def getPromptURL(prompt_id=None, clone=False):
    return makeRoute('prompts', prompt_id, 'clone') if clone else makeRoute('prompts', prompt_id)

def getCorpusURL(corpus_id=None):
    return makeRoute('corpora', corpus_id)

def getTrainingAnswerURL(answer_id=None):
    return makeRoute('training-answers', answer_id)

def getResolvedScoreURL(resolved_score_id=None):
    return makeRoute('resolved-scores', resolved_score_id)

def getHumanScoreURL(human_score_id=None):
    return makeRoute('human-scores', human_score_id)

def getAnswerURL(answer_id=None, share=False):
    return makeRoute('answers', answer_id, 'share') if share else makeRoute('answers', answer_id)

def getAnswerSetURL(answer_set_id=None, answers=False, user=False, share=False):
    ''' answers has priority over share. '''
    if answers:
        return makeRoute('answer-sets', answer_set_id, 'answers/user') if user else makeRoute('answer-sets', answer_set_id, 'answers')
    elif share:
        return makeRoute('answer-sets', answer_set_id, 'share')
    else:
        return makeRoute('answer-sets', answer_set_id)

def getPredictionResultURL(prediction_result_id=None, share=False):
    return makeRoute('prediction-results', prediction_result_id, 'share') if share else makeRoute('prediction-results', prediction_result_id)

def getTrainedModelURL(trained_model_id=None):
    return makeRoute('trained-models', trained_model_id)

def getTrainedModelEvaluationURL(trained_model_evaluation_id=None):
    return makeRoute('trained-model-evaluations', trained_model_evaluation_id)

# Tags
def getAnswerSetTags():
    return makeRoute('tags', None, 'answer-sets')

def getAnswerSetTags():
    return makeRoute('tags', None, 'prompts')

# S3
def getCorpusUploadParametersURL():
    return makeRoute('corpus-upload-parameters')

def getAnswerSetUploadParametersURL():
    return makeRoute('answerset-upload-parameters')

# Tasks
def getCorpusUploadTaskURL(corpus_task_id=None, process=False):
    return makeRoute('corpus-upload-tasks', corpus_task_id, 'process') if process else makeRoute('corpus-upload-tasks', corpus_task_id)

def getAnswerSetUploadTaskURL(answerset_task_id=None, process=False):
    return makeRoute('answerset-upload-tasks', answerset_task_id, 'process') if process else makeRoute('answerset-upload-tasks', answerset_task_id)

def getTrainingTaskURL(training_task_id=None, process=False):
    return makeRoute('training-tasks', training_task_id, 'process') if process else makeRoute('training-tasks', training_task_id)

def getPredictionTaskURL(prediction_task_id=None, process=False):
    return makeRoute('prediction-tasks', prediction_task_id, 'process') if process else makeRoute('prediction-tasks', prediction_task_id)

# Response helpers
def checkStatus(response, successCodes, errorText):
    if response.status_code not in successCodes:
        raise requests.exceptions.RequestException("Code " + str(response.status_code) + ": " + errorText + '\n' + response.content)

