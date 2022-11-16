import os

import numpy as np
import pandas as pd
import spacy
from sense2vec import Sense2VecComponent
from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load('en_core_web_lg')
# s2v = Sense2VecComponent(nlp.vocab).from_disk("/Users/user/Downloads/accord-main/s2v_reddit_2019_lg")
# nlp.add_pipe(s2v)
s2v = nlp.add_pipe("sense2vec")
s2v.from_disk("/Users/user/Downloads/accord-main/s2v_reddit_2019_lg")


def mean_tfidf(userid, words):
    if not os.path.exists('vectors/word/' + userid + '.npy'):
        tokens = [item for sublist in words for item in sublist]
        word2vec = {}
        tfidf = TfidfVectorizer()
        all_words = set(word for word in tokens)

        tfidf.fit(tokens)
        word2weight = dict(zip(tfidf.get_feature_names(), tfidf.idf_))
        print('Weights computed')
        for word in all_words:
            try:
                doc = nlp(word)
                data_type = doc[0]._.s2v_vec.dtype
                word2vec[word] = doc[0]._.s2v_vec
            except AttributeError:
                word2vec[word] = np.zeros((300,), dtype='float32')

        print('Vectors computed')
        mean_vec = []
        for w in tokens:
            try:
                weighted_vec = word2vec[w] * word2weight[w]
                mean_vec.append(weighted_vec)
            except:
                mean_vec.append(np.zeros((300,), dtype='float32'))

        print("Got weighted vectors")
        mean_vec_tfidf = np.array([np.mean(mean_vec, axis=0)])
        # mean_vec_tfidf = np.array([np.mean([word2vec[w] * word2weight[w] for w in tokens], axis=0)])
        np.save('vectors/word/' + userid + '.npy', mean_vec_tfidf)
        print('Vector saved')
        #print(mean_vec_tfidf)
        return mean_vec_tfidf
    else:
        print("Vector already exists")


def get_bert(userid, corpus):
    if not os.path.exists('vectors/sentence/' + userid + '.npy'):
        import tensorflow_hub as hub
        embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
        print("Get the vectors of tweets")
        vectors = [embed([tweet]) for tweet in corpus]
        vectors = np.array(vectors)
        print("Get the average of vectors")
        mean_vec_bert = np.array([np.mean(vectors, axis=0)])
        np.save('vectors/sentence/' + userid + '.npy', mean_vec_bert)
        print('Bert vector saved')
        return mean_vec_bert
    else:
        print("Vector already exists")

        
def get_pron(text):
    doc = nlp(text)
    for token in doc:
        if token.pos_ == 'PRON':
            return token
    return ""
