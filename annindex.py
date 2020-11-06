import annoy
import faiss

class AnnoyIndex():
    def __init__(self, vectors, labels):
        self.dimension = vectors.shape[1]
        self.vectors = vectors.astype('float32')
        self.labels = labels

    def build(self, number_of_trees=10):
        self.index = annoy.AnnoyIndex(self.dimension)
        for i, vec in enumerate(self.vectors):
            self.index.add_item(i, vec.tolist())
        self.index.build(number_of_trees)

    def query(self, vector, k=10):
        indices = self.index.get_nns_by_vector(
            vector.tolist(),
            k,
            search_k=search_in_x_trees)
        return [self.labels[i] for i in indices]


class LSHIndex():
    def __init__(self, vectors, labels):
        self.dimension = vectors.shape[1]
        self.vectors = vectors.astype('float32')
        self.labels = labels

    def build(self, num_bits=8):
        self.index = faiss.IndexLSH(self.dimension, num_bits)
        self.index.add(self.vectors)

    def query(self, vectors, k=10):
        distances, indices = self.index.search(vectors, k)
        # I expect only query on one vector thus the slice
        return [self.labels[i] for i in indices[0]]
