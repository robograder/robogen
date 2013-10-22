class Essay:
    def __init__(self, essay_id, prompt_id, text):
        self.essay_id = essay_id
        self.prompt_id = prompt_id
        self.text = text
        self.scores = {}

    def assignScore(self, key, value):
        self.scores[key] = value
    
    def getScore(self, key):
        return self.scores[key] if key in self.scores else None
    
    def __hash__(self):
        return essay_id

class GeneratedEssay(Essay):
    def __init__(self, essay_id, prompt_id, text, parent_id, generator_id):
        self.essay_id = essay_id
        self.prompt_id = prompt_id
        self.text = text
        self.scores = {}
        self.parent_id = parent_id
        self.generator_id = generator_id

