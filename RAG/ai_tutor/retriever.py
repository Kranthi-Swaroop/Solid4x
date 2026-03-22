from ai_tutor.embeddings import get_query_embedding
from ai_tutor.vector_store import VectorStore
from ai_tutor.bm25_index import BM25Index

class HybridRetriever:
    def __init__(self):
        self.vector_store = VectorStore()
        self.bm25 = BM25Index()
        self.bm25.load()

    def vector_search(self, query, top_k=20, where_filter=None):
        embedding = get_query_embedding(query)
        results = self.vector_store.search(embedding, top_k=top_k, where_filter=where_filter)
        hits = []
        for i in range(len(results["ids"][0])):
            hits.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i]
            })
        return hits

    def bm25_search(self, query, top_k=20, metadata_filter=None):
        results = self.bm25.search(query, top_k=top_k * 2)
        if metadata_filter:
            filtered = []
            for r in results:
                match = True
                if "subject" in metadata_filter and r["metadata"].get("subject") != metadata_filter["subject"]:
                    match = False
                if "class_level" in metadata_filter and r["metadata"].get("class_level") != metadata_filter["class_level"]:
                    match = False
                if "book_hint" in metadata_filter:
                    if metadata_filter["book_hint"].lower() not in r["metadata"].get("source_file", "").lower():
                        match = False
                if match:
                    filtered.append(r)
            results = filtered
        return results[:top_k]

    def reciprocal_rank_fusion(self, result_lists, k=60):
        scores = {}
        doc_map = {}
        for results in result_lists:
            for rank, doc in enumerate(results):
                doc_id = doc["id"]
                if doc_id not in scores:
                    scores[doc_id] = 0
                scores[doc_id] += 1 / (k + rank + 1)
                doc_map[doc_id] = doc

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        return [
            {**doc_map[doc_id], "rrf_score": scores[doc_id]}
            for doc_id in sorted_ids
        ]

    def search(self, query, top_k=15, metadata_filter=None):
        chromadb_filter = None
        if metadata_filter:
            conditions = []
            if "subject" in metadata_filter:
                conditions.append({"subject": {"$eq": metadata_filter["subject"]}})
            if "class_level" in metadata_filter:
                conditions.append({"class_level": {"$eq": metadata_filter["class_level"]}})
            if conditions:
                chromadb_filter = conditions[0] if len(conditions) == 1 else {"$and": conditions}

        vector_results = self.vector_search(query, top_k=20, where_filter=chromadb_filter)
        bm25_results = self.bm25_search(query, top_k=20, metadata_filter=metadata_filter)
        fused = self.reciprocal_rank_fusion([vector_results, bm25_results])
        return fused[:top_k]
