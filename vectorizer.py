import numpy as np
import tensorflow_hub as hub
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load("en_core_web_lg")

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")

def get_mean_tfidf(tokens):
    word2vec = {}
    word2weight = {}
    tfidf = TfidfVectorizer()
    all_words = set(word for word in tokens)

    tfidf.fit(tokens)
    word2weight = dict(zip(tfidf.get_feature_names(), tfidf.idf_))

    for word in all_words:
        word2vec[word] = nlp(word).vector

    mean_vec_tfidf = np.array([np.mean([word2vec[w] * word2weight[w] for w in tokens], axis=0)])
    return mean_vec_tfidf

def get_mean_transformer(corpus):
    vectors = [embed([tweet]) for tweet in corpus]
    vectors = np.array(vectors)
    mean_vec_transformer = np.array([np.mean(vectors, axis=0)])
    return mean_vec_transformer
