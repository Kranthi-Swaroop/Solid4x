import pickle
from rank_bm25 import BM25Okapi
from ai_tutor.config import BM25_PATH


class BM25Index:
    def __init__(self):
        self.index = None
        self.chunk_ids = []
        self.chunk_texts = []
        self.chunk_metadatas = []

    def build(self, chunks):
        self.chunk_ids = [c["id"] for c in chunks]
        self.chunk_texts = [c["contextualized_text"] for c in chunks]
        self.chunk_metadatas = [c["metadata"] for c in chunks]
        tokenized = [text.lower().split() for text in self.chunk_texts]
        self.index = BM25Okapi(tokenized)

    def save(self, path=None):
        path = path or BM25_PATH
        with open(path, 'wb') as f:
            pickle.dump({
                "chunk_ids": self.chunk_ids,
                "chunk_texts": self.chunk_texts,
                "chunk_metadatas": self.chunk_metadatas,
                "index": self.index
            }, f)

    def load(self, path=None):
        path = path or BM25_PATH
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.chunk_ids = data["chunk_ids"]
        self.chunk_texts = data["chunk_texts"]
        self.chunk_metadatas = data["chunk_metadatas"]
        self.index = data["index"]

    def search(self, query, top_k=20):
        tokens = query.lower().split()
        scores = self.index.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            {
                "id": self.chunk_ids[i],
                "text": self.chunk_texts[i],
                "metadata": self.chunk_metadatas[i],
                "score": float(scores[i])
            }
            for i in top_indices if scores[i] > 0
        ]
