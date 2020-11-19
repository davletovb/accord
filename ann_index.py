from annoy import AnnoyIndex
import os
import numpy as np
import json
#import faiss

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


def build_index(sub):
    if sub == 'word':
        d = 300
    else:
        d = 512

    a = AnnoyIndex(d, 'angular')
    index_map = {}

    with os.scandir('vectors/'+sub+'/') as entries:
        for i, entry in enumerate(entries):
            #if (entry.name != "index.ann") and (entry.name != "index_map.json"):
            vec = np.load('vectors/'+sub+'/' + entry.name)
            print(entry.name)
            print(vec)
            a.add_item(i, vec[0])
            index_map[i] = entry.name

    with open('vectors/index_'+sub+'_map.json', 'w') as file:
        json.dump(index_map, file, sort_keys=True, indent=4)

    a.build(10)
    a.save('vectors/index_'+sub+'.ann')
    print('ANN index built')


def search_index(userid, sub):
    if sub == 'word':
        d = 300
    else:
        d = 512

    a = AnnoyIndex(d, 'angular')
    with open('vectors/index_'+sub+'_map.json', 'r') as file:
        index_map = json.load(file)

    user_index = list(index_map.keys())[list(index_map.values()).index(userid + '.npy')]
    a.load('vectors/index_'+sub+'.ann')
    neighbors = a.get_nns_by_item(int(user_index), 5)
    users = [index_map[str(n)].replace('.npy', '.json') for n in neighbors]
    result = []

    for user in users:
        with open('users/'+user, 'r') as file:
            user_profile = json.load(file)
        result.append(user_profile)

    return result
