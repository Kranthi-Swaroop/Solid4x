from sentence_transformers import CrossEncoder

_reranker = None
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def _get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def rerank(query, documents, top_k=5):
    model = _get_reranker()
    pairs = [[query, doc["text"]] for doc in documents]
    scores = model.predict(pairs)
    scored_docs = []
    for i, doc in enumerate(documents):
        scored_docs.append({**doc, "rerank_score": float(scores[i])})
    scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored_docs[:top_k]
