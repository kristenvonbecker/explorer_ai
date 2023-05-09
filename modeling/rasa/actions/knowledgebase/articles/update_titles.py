import os
import time
import json
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss


article_url = 'https://syndication.api.eb.com/production/articles?articleTypeId=1&page='

json_headers = {
    'x-api-key': os.getenv('EB_API_KEY_ADV'),
    'content-type': 'application/json'
}


# get encyclopedia metadata (articleId, title, lastUpdated)

def get_eb_metadata(dir_path='.'):
    article_metadata = []

    code = 200
    page = 1

    url = article_url + str(page)
    response = requests.get(url, headers=json_headers)

    while code == 200 and page < 100:
        this_data = json.loads(response.text)['articles']
        article_metadata += this_data
        page += 1
        url = article_url + str(page)
        response = requests.get(url, headers=json_headers)
        code = response.status_code

    if article_metadata:
        print('Metadata update successful')

    df = pd.DataFrame(data=article_metadata,
                      columns=['articleId', 'title', 'lastUpdated']
                      ).set_index('articleId')

    df.drop(df[df['title'] == ''].index, inplace=True)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    filepath = os.path.join(dir_path, 'metadata.csv')

    df.to_csv(filepath, index_label='articleId')

    archive_path = os.path.join(dir_path, 'metadata_archive')
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)

    timestamp = time.strftime("%Y_%m_%d")

    archive_filepath = os.path.join(archive_path, f'{timestamp}.zip')
    if os.path.exists(archive_filepath):
        os.remove(archive_filepath)

    compression_options = dict(method='zip', archive_name=f'{timestamp}.csv')
    df.to_csv(archive_filepath, index_label='articleId', compression=compression_options)

    if os.path.exists(filepath):
        print(f'Metadata saved at {os.path.abspath(filepath)}')

    return df


def make_indices(metadata, dir_path='.'):

    # get unique article titles and index them
    article_titles = list(set(metadata['title'].tolist()))
    title_index = pd.DataFrame(data=article_titles, columns=['title'])

    # instantiate a sentence transformer
    encoder = SentenceTransformer('all-mpnet-base-v2', device='cpu')

    # get title embeddings
    title_embeddings = encoder.encode(article_titles, device='cpu')

    # build FAISS index
    dim = title_embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(title_embeddings)

    # write indeces to disk

    index_path = os.path.join(dir_path, 'index.bin')
    faiss.write_index(index, index_path)

    title_index_path = os.path.join(dir_path, 'title_index.csv')
    title_index.to_csv(title_index_path, columns=['title'])

    return index, title_index


if __name__ == 'main':

    article_url = 'https://syndication.api.eb.com/production/articles?articleTypeId=1&page='

    json_headers = {
        'x-api-key': os.getenv('EB_API_KEY_ADV'),
        'content-type': 'application/json'
    }

    metadata = get_eb_metadata()
    make_indices(metadata=metadata)
