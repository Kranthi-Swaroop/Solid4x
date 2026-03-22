import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tutor.config import CHUNKS_CACHE
from ai_tutor.ingest import process_new_pdfs, process_all_pdfs, save_chunks, load_chunks
from ai_tutor.embeddings import get_embeddings
from ai_tutor.vector_store import VectorStore
from ai_tutor.bm25_index import BM25Index


def full_reindex():
    start = time.time()
    print("Full reindex: Extracting and chunking all PDFs...")
    chunks = process_all_pdfs()
    save_chunks(chunks)
    print(f"  {len(chunks)} chunks created in {time.time() - start:.1f}s\n")

    t = time.time()
    print("Generating embeddings...")
    texts = [c["contextualized_text"] for c in chunks]
    embeddings = get_embeddings(texts)
    print(f"  {len(embeddings)} embeddings in {time.time() - t:.1f}s\n")

    t = time.time()
    print("Storing in ChromaDB...")
    store = VectorStore()
    store.reset()
    store.add_documents(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=[c["contextualized_text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks]
    )
    print(f"  {store.count()} chunks indexed in {time.time() - t:.1f}s\n")

    t = time.time()
    print("Building BM25 index...")
    bm25 = BM25Index()
    bm25.build(chunks)
    bm25.save()
    print(f"  BM25 index built in {time.time() - t:.1f}s\n")

    print(f"Full reindex complete. Total time: {time.time() - start:.1f}s")


def incremental_index():
    start = time.time()
    new_chunks = process_new_pdfs()

    if not new_chunks:
        return

    t = time.time()
    print("Generating embeddings for new chunks...")
    texts = [c["contextualized_text"] for c in new_chunks]
    embeddings = get_embeddings(texts)
    print(f"  {len(embeddings)} embeddings in {time.time() - t:.1f}s\n")

    t = time.time()
    print("Adding to ChromaDB...")
    store = VectorStore()
    store.add_documents(
        ids=[c["id"] for c in new_chunks],
        embeddings=embeddings,
        documents=[c["contextualized_text"] for c in new_chunks],
        metadatas=[c["metadata"] for c in new_chunks]
    )
    print(f"  {store.count()} total chunks in ChromaDB ({time.time() - t:.1f}s)\n")

    t = time.time()
    print("Rebuilding BM25 index...")
    all_chunks = load_chunks()
    bm25 = BM25Index()
    bm25.build(all_chunks)
    bm25.save()
    print(f"  BM25 index rebuilt with {len(all_chunks)} chunks ({time.time() - t:.1f}s)\n")

    print(f"Incremental indexing complete. Total time: {time.time() - start:.1f}s")


def main():
    if "--full" in sys.argv:
        full_reindex()
    else:
        incremental_index()


if __name__ == "__main__":
    main()
