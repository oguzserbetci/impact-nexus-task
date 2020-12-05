import spacy
from spacy.tokens import Doc, Span, Token
from dataclasses import dataclass, field
import re
from pathlib import Path
import json
import os
import argparse


URL_REGEX = r"https?://.*/[^/]*(about)[^/]*$"
MISSION_WORDS = ("mission", "vision", "idea", "goal", "solve", "believe")


def get_webpage_with_regex(scrape, regex):
    contents = []
    for page_url, content in (
        scrape.get("website", {}).get("website_content", {}).items()
    ):
        if re.findall(regex, page_url):
            contents.append(Content(page_url, content, "website"))
    return contents


def get_twitter_content(scrape):
    contents = []
    for dic in scrape.get("Twitter_account", []):
        contents.append(Content(dic["id_str"], dic["text"], "twitter"))
    return contents


def get_medium_content(scrape):
    contents = []
    for dic in scrape.get("medium", []):
        contents.append(Content(dic["url"], dic["text"], "medium"))
    return contents


@dataclass
class Content:
    identifier: str
    content: str
    source: str
    doc: Doc = field(init=False)

    def __post_init__(self):
        self.doc = nlp(self.content)

    def get_sentences(self):
        return self.doc.sents

    def get_mission_sentences(self):
        return [s for s in self.get_sentences() if s._.has_mission_word]


def get_contents(scrape):
    scrape_contents = []
    index_regex = r"https?://[^/]+/?$"
    scrape_contents += get_webpage_with_regex(scrape, index_regex)
    scrape_contents += get_webpage_with_regex(scrape, URL_REGEX)
    scrape_contents += get_twitter_content(scrape)
    scrape_contents += get_medium_content(scrape)
    return scrape_contents


def get_scrapes(path):
    for json_path in Path(path).glob("*.json"):
        with open(json_path) as f:
            scrape = json.load(f)
            scrape["json_path"] = str(json_path)
            company = scrape["website"]["company_name"]
            yield (company, scrape)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract mission from scrapes.')

    parser.add_argument('--input', default='data/')
    parser.add_argument('--output', default='output/')

    args = parser.parse_args()
    os.makedirs(args.output + "/missions/", exist_ok=True)

    nlp = spacy.load("en_core_web_md")

    is_mission_getter = lambda token: token.lemma_.lower() in MISSION_WORDS
    has_mission_getter = lambda obj: any(
        [t.lemma_.lower() in MISSION_WORDS for t in obj]
    )

    Token.set_extension("is_mission_word", getter=is_mission_getter)
    Span.set_extension("has_mission_word", getter=has_mission_getter)

    for company, scrape in get_scrapes(args.input):
        contents = get_contents(scrape)
        all_mission_sentences = [c.get_mission_sentences() for c in contents]
        flattened_mission_sentences = sum(all_mission_sentences, [])
        with open(f"{args.output}/missions/{company}", "w") as f:
            for sentence in flattened_mission_sentences:
                f.write(str(sentence) + "\n")
