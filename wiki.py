
import attr
import re
import tempfile

import requests
import json

import matplotlib.pyplot as plt

from mediawiki import MediaWiki

from download import get_page
from sentence_tokenizer import Sentences, tokenize, iou
from string_alignment import LookupInString

API = "https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&prop=pageimages&piprop=original&titles=%s"

@attr.s
class Section:
    head = attr.ib()
    mediawiki = attr.ib()
    plaintext = attr.ib()
    images = attr.ib()

    @staticmethod
    def create(mediawiki, text):
        assert mediawiki.head == text.head
        images = list(section_images(mediawiki.text, text.text))
        return Section(text.head, mediawiki.text, Sentences.create(text.text), images)

    def image_scores(self, image):
        return [iou(sent.words, image.caption_words) for sent in self.plaintext.sentences]

    def image_best_locations(self, forward_rad=1, backward_rad=0):
        images_to_process = list(self.images)
        scores = [self.image_scores(image) for image in self.images]

        location_map = []
        valid_locations = set(range(len(self.plaintext.sentences)))
        while images_to_process:
            image_idx = max(
                range(len(scores)),
                key=lambda i: max(score for j, score in enumerate(scores[i]) if j in valid_locations)
            )
            location = max(valid_locations, key=lambda j: scores[image_idx][j])
            location_map.append((location, images_to_process[image_idx]))
            images_to_process.pop(image_idx)
            scores.pop(image_idx)
            valid_locations -= set(range(location - backward_rad, location + forward_rad + 1))
        return sorted(location_map)

@attr.s
class SectionText:
    head = attr.ib()
    text = attr.ib()

@attr.s
class Image:
    path = attr.ib()
    caption = attr.ib()
    location_in_section = attr.ib()

    @property
    def caption_words(self):
        return tokenize(self.caption)

    @property
    def url(self):
        response = requests.get(API % self.path)
        data = json.loads(response.content.decode('utf-8'))
        [page] = data['query']['pages']
        return page['original']['source']

    @property
    def data(self):
        ext = self.path.split(".")[-1]
        data = requests.get(self.url).content
        with tempfile.NamedTemporaryFile(suffix = "." + ext) as f:
            f.write(data)
            return plt.imread(f.name)

def split_by_section(text):
    starts = [0]
    ends = []
    headers = [None]
    for match in re.finditer(r"\n=+(.*[^=])=+\n", text):
        starts.append(match.end())
        ends.append(match.start())
        headers.append(match.group(1).strip())
    ends.append(len(text))
    return [
        SectionText(head, text[start_idx:end_idx])
            for head, start_idx, end_idx in zip(headers, starts, ends)
    ]

def section_images(mediawiki, text):
    lookup = LookupInString(mediawiki, text)

    for match in re.finditer(r"\[\[File[^|]*\|.*\|", mediawiki):
        location = 2 + match.start()
        brackets = 2
        while brackets > 0:
            if mediawiki[location] == "[":
                brackets += 1
            if mediawiki[location] == "]":
                brackets -= 1
            location += 1
        image_tag = mediawiki[match.start():location]
        path, *_, caption = image_tag[2:-2].split("|")
        location_in_section = lookup(match.start())
        yield Image(path, caption, location_in_section)

class Wikipage:
    def __init__(self, title):
        self.title = title
        self.mediawiki = get_page(title)
        self.text = MediaWiki().page(title).content
        self.sections = [
            Section.create(mediawiki, text)
            for mediawiki, text in zip(split_by_section(self.mediawiki), split_by_section(self.text))
        ]
        self.sections[0].head = self.title
    @property
    def all_sentences(self):
        for section in self.sections:
            if section.head in {"References", "Further Reading"}:
                break
            for sentence in section.plaintext.sentences:
                yield sentence.text
