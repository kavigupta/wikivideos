
import attr
import nltk
import re

nltk.download('punkt')
SENT_DETECTOR = nltk.data.load('tokenizers/punkt/english.pickle')
STOPWORDS = set(nltk.corpus.stopwords.words('english'))

def tokenize(text):
    words = [word.lower() for word in nltk.word_tokenize(text) if re.match("^[a-zA-Z]+$", word)]
    return set(words) - STOPWORDS

@attr.s
class Sentence:
    text = attr.ib()
    start = attr.ib()
    end = attr.ib()
    @property
    def words(self):
        return tokenize(self.text)

@attr.s
class Sentences:
    text = attr.ib()
    sentences = attr.ib()

    @staticmethod
    def create(text):
        sentences = SENT_DETECTOR.sentences_from_text(text)
        boundaries = [0]
        for sentence in sentences:
            boundaries.append(boundaries[-1] + len(sentence))
        sentences = [Sentence(sliced, start, end) for sliced, start, end in zip(sentences, boundaries, boundaries[1:])]
        return Sentences(text, sentences)
