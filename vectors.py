import os
from annoy import AnnoyIndex
import numpy as np
import json
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load('en_core_web_lg')
s2v = nlp.add_pipe("sense2vec")
s2v.from_disk("s2v_reddit_2019_lg")


class TextVectorizer:
    def __init__(self):
        self.vectors = []
        self.index = VectorIndex()

    def calculate_vector(self, userid, words) -> np.ndarray:

        if not os.path.exists('vectors/word/'):
            os.makedirs('vectors/word/')

        if not os.path.exists('vectors/word/' + userid + '.npy'):
            tokens = [item for sublist in words for item in sublist]
            word2vec = {}
            tfidf = TfidfVectorizer()
            all_words = set(word for word in tokens)

            tfidf.fit(tokens)
            # get_feature_names will be deprecated, use get_feature_names_out instead
            word2weight = dict(zip(tfidf.get_feature_names_out(), tfidf.idf_))
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
            np.save('vectors/word/' + userid + '.npy', mean_vec_tfidf)
            print('Vector saved')
            return mean_vec_tfidf
        else:
            print("Vector already exists")

    def calculate_vector_bert(userid, corpus) -> np.ndarray:
        
        if not os.path.exists('vectors/sentence/'):
            os.makedirs('vectors/sentence/')
        
        if not os.path.exists('vectors/sentence/' + userid + '.npy'):
            import tensorflow_hub as hub
            embed = hub.load(
                "https://tfhub.dev/google/universal-sentence-encoder-large/5")
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

    def save_vector(self, text: str, vector: np.ndarray):
        # Save the given vector representation of the given text
        self.vectors.append((text, vector))
        self.index.add_vector(text, vector)


class VectorIndex:
    def __init__(self, sub='word'):

        self.sub = sub

        if sub == 'word':
            self.dimension = 300
        else:
            self.dimension = 512

        self.index = AnnoyIndex(self.dimension, 'angular')

        self.index_map = {}

    def add_user(self):

        if not os.path.exists('vectors'):
            os.makedirs('vectors')

        print('Adding new users vector into the index')
        with os.scandir('vectors/'+self.sub+'/') as entries:
            for i, entry in enumerate(entries):
                vec = np.load('vectors/'+self.sub+'/' + entry.name)
                self.index.add_item(i, vec[0])
                self.index_map[i] = entry.name

        with open('vectors/index_'+self.sub+'_map.json', 'w') as file:
            json.dump(self.index_map, file, sort_keys=True, indent=4)

        self.index.build(10)
        self.index.save('vectors/index_'+self.sub+'.ann')
        print('ANN index built')

    def search(self, userid):

        with open('vectors/index_'+self.sub+'_map.json', 'r') as file:
            self.index_map = json.load(file)

        user_index = list(self.index_map.keys())[list(
            self.index_map.values()).index(userid + '.npy')]
        self.index.load('vectors/index_'+self.sub+'.ann')
        neighbors = self.index.get_nns_by_item(int(user_index), 6)
        users = [self.index_map[str(n)].replace(
            '.npy', '.json') for n in neighbors]
        result = []

        for user in users:
            with open('users/'+user, 'r') as file:
                user_profile = json.load(file)
            result.append(user_profile)

        return result[1:]  # remove the user itself


# class AnnoyIndex:
#     def __init__(self, vectors, labels):
#         self.dimension = vectors.shape[1]
#         self.vectors = vectors.astype('float32')
#         self.labels = labels
#
#     def build(self, number_of_trees=5):
#         self.index = annoy.AnnoyIndex(self.dimension)
#         for i, vec in enumerate(self.vectors):
#             self.index.add_item(i, vec.tolist())
#         self.index.build(number_of_trees)
#
#     def query(self, vector, k=10):
#         indices = self.index.get_nns_by_vector(
#             vector.tolist(),
#             k,
#             search_k=5)
#         return [self.labels[i] for i in indices]
#
#
#import faiss
#
# class LSHIndex:
#     def __init__(self, vectors, labels):
#         self.dimension = vectors.shape[1]
#         self.vectors = vectors.astype('float32')
#         self.labels = labels
#
#     def build(self, num_bits=8):
#         self.index = faiss.IndexLSH(self.dimension, num_bits)
#         self.index.add(self.vectors)
#
#     def query(self, vectors, k=10):
#         distances, indices = self.index.search(vectors, k)
#         # I expect only query on one vector thus the slice
#         return [self.labels[i] for i in indices[0]]
