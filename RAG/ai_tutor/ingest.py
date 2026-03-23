import re
import os
import json
import concurrent.futures
import fitz
from pathlib import Path
from ai_tutor.config import JEE_DIR, CHUNK_SIZE, CHUNK_OVERLAP, CHUNKS_CACHE, SUBJECTS, CLASS_LEVELS

INDEX_STATE_FILE = Path(__file__).parent.parent / "index_state.json"

NOISE_PATTERNS = [
    re.compile(r'downloaded\s+from\s+\S+', re.IGNORECASE),
    re.compile(r'www\.\S+\.(com|in|org|net|edu)', re.IGNORECASE),
    re.compile(r'https?://\S+', re.IGNORECASE),
    re.compile(r'(?:ph|phone|mob|tel)[.:\s]*[\d\s\-+()]{7,}', re.IGNORECASE),
    re.compile(r'office[.:]\s*[\w\s,/-]{5,60}', re.IGNORECASE),
    re.compile(r'ranchi|coaching|newton|malik', re.IGNORECASE),
]

CHAPTER_PATTERNS = [
    re.compile(r'^\s*(?:CHAPTER|Chapter)\s+(\d+)\s*[:\-]?\s*(.{0,80})$', re.MULTILINE),
    re.compile(r'^\s*(\d+)\s*[:\-]\s*([A-Z][A-Za-z\s,&()]{4,60})\s*$', re.MULTILINE),
    re.compile(r'^\s*(\d+\.\d+)\s+([A-Z][A-Za-z\s,&()]{3,60})\s*$', re.MULTILINE),
    re.compile(r'(?:UNIT|Unit|SECTION|Section)\s*(\d+)\s*[:\-]?\s*(.{0,80})', re.MULTILINE),
]

# Book name detection from filename
BOOK_NAME_MAP = {
    "modern abc": "Modern ABC",
    "ncert": "NCERT",
    "cengage": "Cengage",
    "hc verma": "HC Verma",
    "irodov": "Irodov",
    "rd sharma": "RD Sharma",
}


def detect_book_name(filename):
    fname_lower = filename.lower()
    for key, name in BOOK_NAME_MAP.items():
        if key in fname_lower:
            return name
    return "Textbook"


def clean_text(text):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append('')
            continue
        is_noise = False
        for pattern in NOISE_PATTERNS:
            if pattern.search(stripped):
                is_noise = True
                break
        if not is_noise:
            cleaned_lines.append(stripped)
    text = '\n'.join(cleaned_lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'[^\x09\x0a\x0d\x20-\x7e\u00a0-\ufffd]', '', text)
    return text.strip()


def extract_text_from_page(page):
    """Simple full-page text extraction for clean text PDFs."""
    raw = page.get_text("text")
    return clean_text(raw) if raw else ""


def process_page(pdf_path_str, page_num):
    doc = fitz.open(pdf_path_str)
    try:
        page = doc[page_num]
        text = extract_text_from_page(page)
        if len(text) > 50:
            return {"page": page_num + 1, "text": text}
    finally:
        doc.close()
    return None


def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    doc.close()
    pages = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        futures = {executor.submit(process_page, str(pdf_path), i): i for i in range(num_pages)}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                pages.append(res)
    pages.sort(key=lambda x: x["page"])
    return pages


def detect_section(text_head, current_section):
    for pattern in CHAPTER_PATTERNS:
        match = pattern.search(text_head)
        if match:
            num = match.group(1).strip()
            title = match.group(2).strip() if match.lastindex >= 2 else ""
            title = re.sub(r'\s+', ' ', title).strip()
            if title and len(title) > 3:
                return f"Section {num}: {title}"
            return f"Section {num}"
    return current_section


def detect_chapters(pages):
    current_chapter = "Introduction"
    for page_info in pages:
        text_head = page_info["text"][:600]
        current_chapter = detect_section(text_head, current_chapter)
        page_info["chapter"] = current_chapter
    return pages


def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Section-aware chunking — splits at paragraph boundaries, never mid-sentence."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Try to break at paragraph, then sentence, then space
            for sep in ['\n\n', '\n', '. ', ' ']:
                break_point = text.rfind(sep, start + chunk_size // 2, end)
                if break_point > start:
                    end = break_point + len(sep)
                    break
        chunk_text = text[start:end].strip()
        if len(chunk_text) > 50:
            chunks.append(chunk_text)
        start = end - overlap if end < len(text) else len(text)
    return chunks


def get_all_pdf_paths():
    pdf_files = []
    for subject_dir in SUBJECTS:
        for class_level in CLASS_LEVELS:
            pdf_dir = JEE_DIR / subject_dir / class_level
            if pdf_dir.exists():
                for pdf_file in sorted(pdf_dir.glob("*.pdf")):
                    pdf_files.append(pdf_file)
    return pdf_files


def load_index_state():
    if INDEX_STATE_FILE.exists():
        with open(INDEX_STATE_FILE, 'r') as f:
            return json.load(f)
    return {"indexed_files": {}, "next_chunk_id": 0}


def save_index_state(state):
    with open(INDEX_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_file_fingerprint(pdf_path):
    stat = os.stat(pdf_path)
    return f"{stat.st_size}_{stat.st_mtime}"


def find_new_pdfs():
    state = load_index_state()
    all_pdfs = get_all_pdf_paths()
    new_pdfs = []
    for pdf_path in all_pdfs:
        key = str(pdf_path)
        fingerprint = get_file_fingerprint(pdf_path)
        if key not in state["indexed_files"] or state["indexed_files"][key] != fingerprint:
            new_pdfs.append(pdf_path)
    return new_pdfs, state


def process_pdf(pdf_path, start_chunk_id):
    rel = pdf_path.relative_to(JEE_DIR)
    parts = rel.parts
    subject_dir = parts[0]
    class_level = parts[1]
    subject_name = SUBJECTS.get(subject_dir, subject_dir)
    book_name = detect_book_name(pdf_path.name)

    print(f"Processing: {book_name} {subject_dir} Class {class_level} - {pdf_path.name}")
    pages = extract_pdf_text(pdf_path)
    pages = detect_chapters(pages)
    chapter_texts = {}
    for page in pages:
        chapter = page["chapter"]
        if chapter not in chapter_texts:
            chapter_texts[chapter] = {"text": "", "pages": []}
        chapter_texts[chapter]["text"] += page["text"] + "\n"
        chapter_texts[chapter]["pages"].append(page["page"])
    chunks = []
    chunk_id = start_chunk_id
    for chapter, data in chapter_texts.items():
        raw_chunks = split_into_chunks(data["text"])
        for chunk_text in raw_chunks:
            context_prefix = f"[{book_name} | {subject_name} | Class {class_level} | {chapter}]"
            chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": chunk_text,
                "contextualized_text": f"{context_prefix}\n\n{chunk_text}",
                "metadata": {
                    "subject": subject_name,
                    "class_level": class_level,
                    "chapter": chapter,
                    "book_name": book_name,
                    "source_file": pdf_path.name,
                    "page_range": f"{min(data['pages'])}-{max(data['pages'])}"
                }
            })
            chunk_id += 1
    return chunks


def process_all_pdfs():
    all_chunks = []
    chunk_id = 0
    for pdf_path in get_all_pdf_paths():
        new_chunks = process_pdf(pdf_path, chunk_id)
        all_chunks.extend(new_chunks)
        chunk_id += len(new_chunks)
    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks


def process_new_pdfs():
    new_pdfs, state = find_new_pdfs()
    if not new_pdfs:
        print("No new or modified PDFs found.")
        return []
    print(f"Found {len(new_pdfs)} new/modified PDF(s):")
    for p in new_pdfs:
        print(f"  - {p.relative_to(JEE_DIR)}")
    chunk_id = state["next_chunk_id"]
    new_chunks = []
    for pdf_path in new_pdfs:
        pdf_chunks = process_pdf(pdf_path, chunk_id)
        new_chunks.extend(pdf_chunks)
        chunk_id += len(pdf_chunks)
        state["indexed_files"][str(pdf_path)] = get_file_fingerprint(pdf_path)
    state["next_chunk_id"] = chunk_id
    save_index_state(state)
    existing_chunks = load_chunks() if CHUNKS_CACHE.exists() else []
    all_chunks = existing_chunks + new_chunks
    save_chunks(all_chunks)
    print(f"New chunks: {len(new_chunks)} | Total: {len(all_chunks)}")
    return new_chunks


def save_chunks(chunks, path=None):
    path = path or CHUNKS_CACHE
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def load_chunks(path=None):
    path = path or CHUNKS_CACHE
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
