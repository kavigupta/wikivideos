
import attr
import nltk

nltk.download('punkt')
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

@attr.s
class Sentences:
    text = attr.ib()
    sentences = attr.ib()

    @staticmethod
    def create(text):
        return Sentences(text, sent_detector.sentences_from_text(text))
