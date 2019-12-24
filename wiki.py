
import re
import attr

from mediawiki import MediaWiki

from download import get_page
from sentence_tokenizer import Sentences
from string_alignment import LookupInString

@attr.s
class Section:
    head = attr.ib()
    mediawiki = attr.ib()
    plaintext = attr.ib()
    images = attr.ib()

@attr.s
class SectionText:
    head = attr.ib()
    text = attr.ib()

@attr.s
class Image:
    path = attr.ib()
    caption = attr.ib()
    location_in_section = attr.ib()

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
        self.sections = []
        for mediawiki, text in zip(split_by_section(self.mediawiki), split_by_section(self.text)):
            assert mediawiki.head == text.head
            images = list(section_images(mediawiki.text, text.text))
            self.sections.append(Section(text.head, mediawiki.text, Sentences.create(text.text), images))
