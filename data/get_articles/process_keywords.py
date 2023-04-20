import re
import string
from nltk import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from fuzzywuzzy import fuzz, process
from scipy import spatial
import gensim.downloader as api


# PROCESSING KEYWORDS AND ARTICLE TITLES FOR MATCHING

# clean and tokenize text
def clean_tokenize(text, stopwords=None):
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)  # convert multiple spaces to single space
    text = re.sub(r"(?<=\w)-(?=\w)", " ", text)  # problem-solve -> problem solve
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)  # remove punctuation
    tokens = word_tokenize(text)
    if stopwords:
        tokens = [t for t in tokens if t not in stopwords]
    tokens = ["" if t.isdigit() else t for t in tokens]  # remove digits; change this to _convert_?
    tokens = [t for t in tokens if len(t) > 1]  # remove 1-word tokens
    return tokens


# load GloVe model
glove_model = api.load('glove-twitter-25')
zero_vector = np.zeros(glove_model.vector_size)


# convert tokens to word embeddings
def vectorize(tokens):
    features = []
    for token in tokens:
        if token in glove_model:
            try:
                features.append(glove_model[token])
            except KeyError:
                continue
    if not features:
        features.append(zero_vector)
    return features


# define "nearest" titles for a given keyword using two metrics:
# fuzzy matching (using token_sort_ratio)
# GloVe embeddings (using cosine distance)

def find_nearest_titles(keyword, titles=None, title_embeddings=None, method="fuzz-matching", num=3):
    nearest = []
    if method == "fuzz-matching":
        fuzz_matches = process.extract(keyword, titles, limit=num, scorer=fuzz.token_sort_ratio)
        fuzz_matches.sort(key=lambda x: x[1], reverse=True)
        fuzz_scores = [score for match, score in fuzz_matches]
        if any([score >= 90 for score in fuzz_scores]):
            nearest += [match for match, score in fuzz_matches if score >= 90]
    if method == "embedding":
        tokens = clean_tokenize(keyword, stopwords=stopwords.words("english"))
        vectors = np.array(vectorize(tokens))
        avg_vector = np.mean(vectors, axis=0)
        if not all([x == 0 for x in avg_vector]):
            nearest += sorted(title_embeddings.keys(),
                             key=lambda title: spatial.distance.cosine(title_embeddings[title], avg_vector))
            nearest = nearest[:num]
    return nearest
