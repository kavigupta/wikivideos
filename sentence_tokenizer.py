
import attr
import nltk

nltk.download('punkt')
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

@attr.s
class Sentences:
    text = attr.ib()
    sentences = attr.ib()
    boundaries = attr.ib()

    @staticmethod
    def create(text):
        sentences = sent_detector.sentences_from_text(text)
        boundaries = [0]
        for sentence in sentences:
            boundaries.append(boundaries[-1] + len(sentence))
        return Sentences(text, sentences, list(zip(boundaries, boundaries[1:])))
