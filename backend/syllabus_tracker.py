import os
import json
import re
import PyPDF2
from docx import Document
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import models

# -------------------------
# 1. Extract text from uploaded syllabus
# -------------------------
def extract_text(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        text_content = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content += text + "\n"
        return text_content

    elif file_path.lower().endswith(".docx"):
        doc = Document(file_path)  # Changed from docx.Document()
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    else:
        raise ValueError("Unsupported file type. Please upload PDF or DOCX.")

# -------------------------
# 2. Parse syllabus text into structured topics
# -------------------------
def parse_syllabus_to_topics(syllabus_text: str):
    """
    Parses syllabus text into a list of topics/subtopics.
    This version uses regex + simple heuristics (can later be improved with LLM).
    """
    # Split by line breaks, ignoring empty lines
    lines = [line.strip() for line in syllabus_text.split("\n") if len(line.strip()) > 3]

    # Heuristic: treat numbered or bulleted lines as topics
    topics = []
    for line in lines:
        if re.match(r"^\d+\.|^-|•|\*", line):
            cleaned = re.sub(r"^\d+\.|^-|•|\*", "", line).strip()
            topics.append(cleaned)
        elif len(line.split()) < 10:  # short line, likely a topic header
            topics.append(line)

    # Remove duplicates and too-short fragments
    topics = list({t for t in topics if len(t) > 3})
    return topics

# -------------------------
# 3. Compare with lecture topics from database
# -------------------------
def calculate_syllabus_coverage(db: Session, syllabus_topics: list):
    """
    Compares the extracted syllabus topics with all lecture topics_json fields.
    Returns coverage statistics.
    """
    # Fetch topics from all processed lectures
    query = text("""
        SELECT topics_json FROM lectures WHERE status = 'DONE';
    """)
    rows = db.execute(query).fetchall()

    covered_topics = set()
    for row in rows:
        try:
            lecture_topics = json.loads(row[0])
            for t in lecture_topics:
                # t is dict like {"topic": "Programming Paradigms", "subtopics": [...]}
                covered_topics.add(t["topic"].strip().lower())
                for s in t.get("subtopics", []):
                    covered_topics.add(s.strip().lower())
        except Exception:
            continue

    syllabus_set = {t.strip().lower() for t in syllabus_topics}
    matched = [t for t in syllabus_topics if t.strip().lower() in covered_topics]
    missing = [t for t in syllabus_topics if t.strip().lower() not in covered_topics]

    coverage = (len(matched) / len(syllabus_topics) * 100) if syllabus_topics else 0

    return {
        "total_topics": len(syllabus_topics),
        "covered_topics": len(matched),
        "coverage_percentage": round(coverage, 2),
        "missing_topics": missing,
        "matched_topics": matched
    }

# -------------------------
# 4. FastAPI integration
# -------------------------
def process_syllabus_file(file_path: str, db: Session):
    """
    High-level wrapper that handles extraction + comparison.
    """
    syllabus_text = extract_text(file_path)
    syllabus_topics = parse_syllabus_to_topics(syllabus_text)
    result = calculate_syllabus_coverage(db, syllabus_topics)
    return result

# -------------------------
# 5. Save and retrieve results
# -------------------------

RESULTS_DIR = "temp_uploads/syllabus_results"
os.makedirs(RESULTS_DIR, exist_ok=True)


def save_coverage_result(result: dict, filename: str):
    """
    Saves the coverage result JSON for later retrieval.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(filename)[0]
    save_path = os.path.join(RESULTS_DIR, f"{base_name}_{timestamp}.json")

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    return save_path


def get_latest_coverage_result():
    """
    Fetches the most recently generated syllabus coverage JSON.
    """
    files = sorted(
        [f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join(RESULTS_DIR, f)),
        reverse=True,
    )

    if not files:
        return None

    latest_file = os.path.join(RESULTS_DIR, files[0])
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {"filename": files[0], "data": data}