import os
import json
import requests
from bs4.element import Comment
from bs4 import BeautifulSoup
from lxml import html


# define parameters for API calls to the Encyclopedia Britannica products

article_list_url = {
    'advanced': 'https://syndication.api.eb.com/production/articles?articleTypeId=1&page=',
    'science': 'https://syndication.api.eb.com/production/articles?articleTypeId=1&categoryId=2&page=',
    'technology': 'https://syndication.api.eb.com/production/articles?articleTypeId=1&categoryId=2&page='
}

json_header = {
    'advanced': {
        'x-api-key': os.getenv('EB_API_KEY_ADV'),
        'content-type': 'application/json'
    },
    'science': {
        'x-api-key': os.getenv('EB_API_KEY_SCI'),
        'content-type': 'application/json'
    },
    'technology': {
        'x-api-key': os.getenv('EB_API_KEY_TEC'),
        'content-type': 'application/json'
    }
}

xml_header = {
    'advanced': {
        'x-api-key': os.getenv('EB_API_KEY_ADV'),
        'content-type': 'text/xml; charset=UTF-8'
    },
    'science': {
        'x-api-key': os.getenv('EB_API_KEY_SCI'),
        'content-type': 'text/xml; charset=UTF-8'
    },
    'technology': {
        'x-api-key': os.getenv('EB_API_KEY_TEC'),
        'content-type': 'text/xml; charset=UTF-8'
    }
}


# get list of metadata for all entries in each source (e.g. for each encyclopedia article)
def get_encyclopedia_metadata(source="advanced", dir_path=None):
    article_metadata = []

    code = 200
    page = 1

    url = article_list_url[source] + str(page)
    response = requests.get(url, headers=json_header[source])

    while code == 200 and page < 100:
        this_data = json.loads(response.text)['articles']
        article_metadata += this_data
        page += 1
        url = article_list_url[source] + str(page)
        response = requests.get(url, headers=json_header[source])
        code = response.status_code

    path = dir_path
    if not os.path.exists(path):
        os.makedirs(path)

    filepath = os.path.join(path, source + '_metadata.json')
    if os.path.exists(filepath):
        os.remove(filepath)

    with open(filepath, 'w') as outfile:
        json.dump(article_metadata, outfile, indent=2)

    return article_metadata


# get article content (xml) for a given article_id
def get_article_xml(article_id, source="advanced", dir_path=None):
    url = f'https://syndication.api.eb.com/production/article/{str(article_id)}/xml'
    response = requests.get(url, headers=xml_header[source])
    xml_data = BeautifulSoup(response.text, features="xml")
    if dir_path:
        filename = str(article_id) + ".xml"
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "w") as outfile:
            outfile.write(xml_data.prettify())
    return xml_data


# get xml content for a collection of article_ids; save to disk
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


####################################

def tag_visible(element):
    if element.parent.name in [
        'assembly', 'caption', 'credit', 'style', 'script', 'head', 'title', 'meta', '[document]'
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(soup):
    texts = soup.findAll(text=True)
    ps = filter(tag_visible, texts)
    return [p.strip() for p in ps]

####################################
