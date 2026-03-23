import re
from google import genai
from ai_tutor.config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

SUBJECT_KEYWORDS = {
    "physics": "Physics",
    "chemistry": "Chemistry",
    "maths": "Mathematics",
    "math": "Mathematics",
    "mathematics": "Mathematics",
}

BOOK_KEYWORDS = [
    "modern abc", "modern", "abc", "ncert", "cengage",
    "hc verma", "irodov", "resnick", "halliday",
    "morrison", "jd lee", "op tandon", "rd sharma"
]

# Common JEE topics → subject auto-routing
TOPIC_TO_SUBJECT = {
    "electrostatics": "Physics", "coulomb": "Physics", "electric": "Physics",
    "magnetic": "Physics", "optics": "Physics", "thermodynamics": "Physics",
    "kinematics": "Physics", "gravitation": "Physics", "newton": "Physics",
    "wave": "Physics", "oscillation": "Physics", "current": "Physics",
    "capacitor": "Physics", "inductor": "Physics", "resistor": "Physics",
    "friction": "Physics", "momentum": "Physics", "energy": "Physics",
    "organic": "Chemistry", "inorganic": "Chemistry", "reaction": "Chemistry",
    "bond": "Chemistry", "acid": "Chemistry", "base": "Chemistry",
    "oxidation": "Chemistry", "reduction": "Chemistry", "mole": "Chemistry",
    "equilibrium": "Chemistry", "electrochemistry": "Chemistry",
    "polymer": "Chemistry", "alkane": "Chemistry", "alkene": "Chemistry",
    "aromatic": "Chemistry", "sn1": "Chemistry", "sn2": "Chemistry",
    "integral": "Mathematics", "derivative": "Mathematics", "matrix": "Mathematics",
    "vector": "Mathematics", "probability": "Mathematics", "trigonometry": "Mathematics",
    "limit": "Mathematics", "continuity": "Mathematics", "differential": "Mathematics",
    "conic": "Mathematics", "parabola": "Mathematics", "ellipse": "Mathematics",
    "permutation": "Mathematics", "combination": "Mathematics",
    "determinant": "Mathematics", "sequence": "Mathematics", "series": "Mathematics",
}


def parse_query_metadata(query):
    query_lower = query.lower()
    filters = {}
    for keyword, subject in SUBJECT_KEYWORDS.items():
        if keyword in query_lower:
            filters["subject"] = subject
            break
    # Auto-detect subject from topic if not explicitly mentioned
    if "subject" not in filters:
        for topic, subject in TOPIC_TO_SUBJECT.items():
            if topic in query_lower:
                filters["subject"] = subject
                break
    class_match = re.search(r'class\s*(\d+)|(\d+)\s*(?:th|st|nd|rd)?\s*class', query_lower)
    if not class_match:
        class_match = re.search(r'(?<!\.)\b(11|12)\b(?!\.)', query_lower)
    if class_match:
        level = class_match.group(1) or class_match.group(2) if class_match.lastindex and class_match.lastindex >= 2 else class_match.group(1)
        if level in ("11", "12"):
            filters["class_level"] = level
    for book in BOOK_KEYWORDS:
        if book in query_lower:
            filters["book_hint"] = book
            break
    page_match = re.search(r'page\s*(\d+)', query_lower)
    if page_match:
        filters["page_hint"] = int(page_match.group(1))
    return filters


def build_chromadb_filter(metadata):
    conditions = []
    if "subject" in metadata:
        conditions.append({"subject": {"$eq": metadata["subject"]}})
    if "class_level" in metadata:
        conditions.append({"class_level": {"$eq": metadata["class_level"]}})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def expand_query(query):
    prompt = (
        "You are a JEE exam tutor. A student asked the following doubt:\n\n"
        f'"{query}"\n\n'
        "Generate exactly 3 search queries that would help find relevant "
        "information from JEE reference books (like Modern ABC, NCERT, Cengage) to answer this doubt. "
        "Each query should capture a different aspect of the question.\n\n"
        "Return ONLY the 3 queries, one per line, no numbering, no explanation."
    )
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
        return [query] + lines[:3]
    except Exception:
        return [query]
