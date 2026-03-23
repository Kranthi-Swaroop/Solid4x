from google import genai
from ai_tutor.config import GEMINI_API_KEY, GEMINI_MODEL
from ai_tutor.retriever import HybridRetriever
from ai_tutor.reranker import rerank
from ai_tutor.query_processor import expand_query, parse_query_metadata

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are an expert JEE tutor helping students with their doubts.
You have access to excerpts from JEE textbooks (e.g., Modern ABC, NCERT).
Use these excerpts to ground your conceptual explanations and cite them.
However, if the student asks you to solve a specific numerical problem, simplify an equation, or derive a standard formula, YOU MUST DO SO using your own expert knowledge, guided by the formulas in the context.
Never refuse to solve a problem just because the exact step-by-step solution isn't in the provided text.

Rules:
- Give clear, step-by-step explanations and derivations suitable for JEE preparation
- Use proper mathematical notation where needed
- Cite the source (Book, Subject, Class, Chapter) when referencing definitions, laws, or formulas from the context
- If solving a mathematical or physics problem, provide the complete working out
- Keep answers focused and highly accurate"""


def build_context(documents):
    context_parts = []
    for i, doc in enumerate(documents):
        meta = doc["metadata"]
        book = meta.get("book_name", meta.get("source_file", "Unknown").replace(".pdf", ""))
        source = f"{book} | {meta['subject']} | Class {meta['class_level']} | {meta['chapter']} | Pages {meta.get('page_range', 'N/A')}"
        context_parts.append(f"[Source {i+1}: {source}]\n{doc['text']}")
    return "\n\n---\n\n".join(context_parts)


def format_source(meta):
    book = meta.get("book_name", meta.get("source_file", "Unknown").replace(".pdf", ""))
    return f"{book} | {meta['subject']} Class {meta['class_level']} | {meta['chapter']} | Pages {meta.get('page_range', 'N/A')}"


def generate_answer(query, use_query_expansion=True):
    retriever = HybridRetriever()
    metadata = parse_query_metadata(query)
    if use_query_expansion:
        queries = expand_query(query)
        all_results = []
        seen_ids = set()
        for q in queries:
            results = retriever.search(q, top_k=10, metadata_filter=metadata)
            for r in results:
                if r["id"] not in seen_ids:
                    seen_ids.add(r["id"])
                    all_results.append(r)
    else:
        all_results = retriever.search(query, top_k=15, metadata_filter=metadata)

    if metadata.get("book_hint"):
        book_hint = metadata["book_hint"].lower()
        book_matches = [r for r in all_results if book_hint in r["metadata"].get("source_file", "").lower()]
        if book_matches:
            all_results = book_matches + [r for r in all_results if r not in book_matches]

    reranked = rerank(query, all_results, top_k=5)
    context = build_context(reranked)

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context from textbooks:\n\n{context}\n\n"
        f"---\n\nStudent's Question: {query}\n\n"
        "Provide a detailed, accurate answer based ONLY on the above context. "
        "Cite sources using [Source N] notation."
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "temperature": 0.1,
            "max_output_tokens": 2048,
        }
    )

    sources = []
    for doc in reranked:
        sources.append(format_source(doc["metadata"]))

    return {
        "answer": response.text,
        "sources": list(dict.fromkeys(sources)),
        "num_chunks_retrieved": len(all_results),
        "num_chunks_used": len(reranked),
    }
