
from mediawiki import MediaWiki

import tqdm

from sentence_tokenizer import Sentences
from wiki import split_by_section

from profanityfilter import ProfanityFilter

def all_sentences(*titles):
    for title in titles:
        content = MediaWiki().page(title).content
        sections = split_by_section(content)
        for section in sections:
            for sentence in Sentences.create(section.text).sentences:
                text = sentence.text
                text = text.strip()
                if 100 <= len(text) <= 300 and "\n" not in text and "." not in text[:-1]:
                    yield text

pf = ProfanityFilter()

CATS = "Cat", "Tiger", "Lion", "Cats_and_the_Internet"
BASKETBALL = "Basketball", "Golden_State_Warriors", "California_Memorial_Stadium"
BERKELEY = "Oski_the_Bear", "University_of_California,_Berkeley", "Campus_of_the_University_of_California,_Berkeley"
TYPING = "Typing", "Typewriter"

for s in tqdm.tqdm(sorted(list(all_sentences(*CATS, *BASKETBALL, *BERKELEY, *TYPING)))):
    if pf.is_clean(s):
        print(s)
