from sentence_transformers import SentenceTransformer
from ai_tutor.config import EMBEDDING_MODEL

_model = None
BATCH_SIZE = 256


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def get_embeddings(texts):
    model = _get_model()
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"  Embedding batch {batch_num}/{total_batches} ({len(batch)} texts)")
        embs = model.encode(batch, show_progress_bar=False, normalize_embeddings=True)
        all_embeddings.extend(embs.tolist())
    return all_embeddings


def get_query_embedding(query):
    model = _get_model()
    emb = model.encode(query, normalize_embeddings=True)
    return emb.tolist()
