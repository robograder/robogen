class Word:
    def __init__(self, judgmental, hedge):
        if isinstance(judgmental, int) and -1 <= judgmental <= 1:
            self.judgmental = judgmental 
        else:
            raise ValueError("'Judgmentalness' must be an integer in (-1, 0, 1).")
        if isinstance(hedge, bool):
            self.hedge = hedge
        else:
            raise ValueError("'Hedgeness' must be a boolean.")

class Verb(Word):
    def __init__(self, transitive, judgmental, hedge):
        super(Verb, self).__init__(judgmental, hedge)
        self.partofspeech = 'verb'
        if isinstance(transitive, bool):
            self.transitive = transitive
        else:
            raise ValueError("'Transitivity' must be a boolean.")

