import faiss
from sentence_transformers import SentenceTransformer

import numpy as np
import pandas as pd

import os
import json

import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import re
from unidecode import unidecode
from lxml import html

from .knowledgebase import articles


# define paths
# proj_home = os.getenv("PROJ_HOME")
proj_home = '/Users/vonbecker/ML_Bootcamp_code/Capstone/explorer_ai'
articles_path = os.path.join(proj_home, "modeling/rasa/actions/knowledgebase/articles")

index_filepath = os.path.join(articles_path, "index.bin")
title_index_filepath = os.path.join(articles_path, "title_index.csv")
metadata_filepath = os.path.join(articles_path, "metadata.csv")

# read files
index = faiss.read_index(index_filepath)
title_index = pd.read_csv(title_index_filepath)
metadata = pd.read_csv(metadata_filepath)

# instantiate encoder
encoder = SentenceTransformer('all-mpnet-base-v2', device='cpu')


# get articleId matches for a given subject
def get_article_matches(subject, k=5):
    search_text = [subject]
    search_embedding = encoder.encode(search_text, device='cpu')
    dists, ids = index.search(search_embedding, k=k)
    dists = np.around(np.clip(dists, 0, 1), decimals=4)
    results = pd.DataFrame({'distance': dists[0], 'index': ids[0]})
    merge = pd.merge(results, title_index, left_on='index', right_index=True)
    title_matches = merge['title'].tolist()
    article_matches = []
    for title in title_matches:
        these_ids = metadata['articleId'].loc[metadata['title'] == title].tolist()
        article_matches += [(title, article_id) for article_id in these_ids]
    return article_matches


def get_article_text(article_id, title=None, par_num=0):
    xml = get_article_xml(article_id=article_id)
    paragraphs = get_article_paragraphs(xml_data=xml)
    if par_num == 0:
        text, title, aliases, grouping, is_person = clean_par_0(paragraphs[0], title)
    elif par_num < len(paragraphs):
        text = clean_par_n(paragraphs[par_num])
    else:
        text = ''
    return text


# regex for text processing of article parapgraphs

apos_pattern = r"(\w+)(\s)*'S "
paren_pattern = r"(\((?!born).+?\)),? "
plural_pattern = r"(plural .+?), "
alias_pattern = r"(?:also called|also spelled) (.+?), "
cat_pattern = r"(?!in full)(?:in|In) (.+?), (?:or (.+?), (.+?), )?"
aka_pattern = r"(?:Latin in full|in full|byname of|original name) (.+?), "
bd_pattern = r"\(born (\w+ \d{1,2}, \d{4})(?:, )(.*?)(?:—died (\w+ \d{1,2}, \d{4})(?:, )(.*?))?\), "
x_sp_pattern = r"\s{2,}"
sp_punc_pattern = r"\s+([.,\:\-])"

# header for xml requests

eb_api_key = '8a218da9-f310-4348-800e-2caea12ae5da'

xml_headers = {
    'x-api-key': eb_api_key,
    'content-type': 'text/xml; charset=UTF-8'
}


# helper functions for xml parsing

def tag_visible(element):
    if element.parent.name in [
        'assembly', 'caption', 'credit', 'style', 'script', 'head', 'title', 'meta', '[document]'
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(soup):
    texts = soup.findAll(string=True)
    ps = filter(tag_visible, texts)
    return [p.strip() for p in ps]


# get article content (xml) for a given article_id

def get_article_xml(article_id, dir_path=None):
    url = f'https://syndication.api.eb.com/production/article/{str(article_id)}/xml'
    response = requests.get(url, headers=xml_headers)
    xml_data = BeautifulSoup(response.text, "html.parser")
    if dir_path:
        filename = str(article_id) + ".xml"
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "w") as outfile:
            outfile.write(xml_data.prettify())
    return xml_data


# parse xml into a list of paragraphs; save to disk

def get_article_paragraphs(xml_data, article_id=None, dir_path=None):
    paragraphs = []
    p_tags = xml_data.find_all("p")
    for i in range(len(p_tags)):
        text = text_from_html(p_tags[i])
        paragraphs.append(" ".join(text))
    if dir_path:
        filename = str(article_id) + ".json"
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "w") as outfile:
            json.dump(paragraphs, outfile, indent=2)
    return paragraphs


# process first paragraph

def clean_par_0(paragraph, title, decode=False):
    title = title.strip(" ,")  # strip commas and extra whitespace from titles
    title = title.replace(u"\u2019", "'")  # replace unicode single smart quote in title
    paragraph = paragraph.replace(u"\u2019", "'").strip()  # replace unicode single smart quote in text

    # remove extra spaces
    x_space = re.search(x_sp_pattern, paragraph)
    if x_space:
        paragraph = re.sub(x_space.group(0), " ", paragraph)

    # remove spaces before punctuation
    paragraph = re.sub(r"\s+([.,\:\-])", r"\1", paragraph)

    # unidecode text
    if decode:
        title = unidecode(title)
        paragraph = unidecode(paragraph)

    # convert title to title-case
    title_split = title.split()
    if len(title_split) > 1:
        title_tc = ' '.join([title_split[0].title()] + title_split[1:])
    else:
        title_tc = title.title()

    # convert format of beginning of text; e.g.
    # "expert system, a computer program..." is converted to "Expert system: a computer program..."
    title_comma = re.escape(title) + r"(\s)*,(\s)*"
    title_colon = title_tc + ": "
    paragraph = re.sub(title_comma, title_colon, paragraph)

    prefix = title_colon
    contents = []

    # convert Prisoner'S or Prisoner 'S to Prisoner's
    apos_title = re.search(apos_pattern, title)
    if apos_title:
        title = title.replace(apos_title.group(0), apos_title.group(1) + "'s")
    apos_text = re.search(apos_pattern, paragraph)
    if apos_text:
        paragraph = paragraph.replace(apos_text.group(0), apos_text.group(1) + "'s")

    # collect parenthetical information and format nicely
    # Q: loop this to check for more than one paren group?
    paren_info = re.search(re.escape(prefix) + paren_pattern, paragraph)
    if paren_info:
        contents.append(paren_info.group(1).strip("()"))
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(paren_info.group(0), prefix, 1)

    plural = re.search(re.escape(prefix) + plural_pattern, paragraph)
    if plural:
        contents.append(plural.group(1))
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(plural.group(0), prefix, 1)

    alias_name = re.search(re.escape(prefix) + alias_pattern, paragraph)
    if alias_name:
        contents.append("or " + alias_name.group(1).strip())
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(alias_name.group(0), prefix, 1)
        aliases = [x.strip() for x in alias_name.group(1).split(" or ")]
    else:
        aliases = []

    category = re.search(re.escape(prefix) + cat_pattern, paragraph)
    if category:
        if category.group(3):
            cat_name = category.group(1) + "/" + category.group(2) + " " + category.group(3)
            contents.append("in " + cat_name)
        else:
            cat_name = category.group(1)
            contents.append("in " + cat_name)
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(category.group(0), prefix, 1)
        grouping = [x.strip() for x in cat_name.split(" and ")]
    else:
        grouping = []

    aka_name = re.search(re.escape(prefix) + aka_pattern, paragraph)
    if aka_name:
        contents.append("aka " + aka_name.group(1))
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(aka_name.group(0), prefix, 1)

    birth_death = re.search(re.escape(prefix) + bd_pattern, paragraph)
    if birth_death:
        contents.append("born " + birth_death.group(1) + " in " + birth_death.group(2))
        if birth_death.group(3):
            contents.append("died " + birth_death.group(3) + " in " + birth_death.group(4))
            is_person = 2
        else:
            is_person = 1
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(birth_death.group(0), prefix, 1)
    else:
        is_person = 0

    title_paren_pattern = r"\(.+?\)"
    title_paren_text = re.search(title_paren_pattern, title)
    if title_paren_text:
        title = title.replace(title_paren_text.group(0), '').strip()

    return paragraph, title, aliases, grouping, is_person


# process paragraphs 2+

def clean_par_n(paragraph, decode=False):
    paragraph = paragraph.replace(u"\u2019", "'").strip()  # replace unicode single smart quote in text

    # remove extra spaces
    x_space = re.search(x_sp_pattern, paragraph)
    if x_space:
        paragraph = re.sub(x_space.group(0), " ", paragraph)

    # remove spaces before punctuation
    paragraph = re.sub(r"\s+([.,\:\-])", r"\1", paragraph)

    # unidecode text
    if decode:
        paragraph = unidecode(paragraph)

    # convert Prisoner'S or Prisoner 'S to Prisoner's
    apos_text = re.search(apos_pattern, paragraph)
    if apos_text:
        paragraph = paragraph.replace(apos_text.group(0), apos_text.group(1) + "'s")

    return paragraph
