import json

from app.extensions import db
from app.models.questions import Question
from app.services.files import list_files
from app.services.links import list_links
from app.services.llm import complete


def create_question(user_id, question):
    new_question = Question(user_id=user_id, question=question)
    db.session.add(new_question)
    db.session.commit()
    return new_question.to_dict()


def save_asked_question(user_id, question, answer, labels):
    record = Question(
        user_id=user_id,
        question=question,
        answer=answer,
        labels=json.dumps(labels),
    )
    db.session.add(record)
    db.session.commit()
    return record.to_dict()

def delete_question(user_id, question_id):
    record = Question.query.filter_by(user_id=user_id, id=question_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        return True
    return False

def list_questions(user_id):
    rows = (
        Question.query.filter_by(user_id=user_id)
        .order_by(Question.created_at.desc())
        .all()
    )
    return [row.to_dict() for row in rows]

def passages(text):
    chunks = []
    for piece in text.split("\n\n"):
        piece = piece.strip()
        if not piece:
            continue
        if len(piece) <= 800:
            chunks.append(piece)
            continue
        start = 0
        while start < len(piece):
            chunks.append(piece[start:start + 800])
            start += 700
    return chunks

STOP = {"the", "and", "for", "with", "that", "this", "from"}
def words(text):
    cleaned = []
    for raw in text.lower().split():
        word = "".join(ch for ch in raw if ch.isalnum())
        if len(word) >= 3 and word not in STOP:
            cleaned.append(word)
    return cleaned


def source_label(source):
    if "file_name" in source:
        return "file", f"file: {source['file_name']}"
    return "link", f"link: {source['title']}"


def select_passages(question, sources, limit=8):
    question_words = set(words(question))
    scored = []
    for source in sources:
        kind, label = source_label(source)
        for passage in passages(source["content_text"]):
            score = len(question_words & set(words(passage)))
            if score == 0:
                continue
            scored.append({
                "score": score,
                "source": source,
                "kind": kind,
                "label": label,
                "passage": passage,
            })
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]


def readable_sources(user_id):
    sources = []
    for file in list_files(user_id):
        if file["content_text"] and not file["content_error"]:
            sources.append(file)
    for link in list_links(user_id):
        if link["content_text"] and not link["content_error"]:
            sources.append(link)
    return sources

def ask_model(question, blocks):
    sources = "\n\n".join(blocks)
    prompt = (
        "Answer the question using only the sources below. "
        "Do not list the sources in the answer.\n\n"
        f"{sources}\n\n"
        f"Question: {question}"
    )
    return complete(prompt)
