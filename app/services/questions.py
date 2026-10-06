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
        "Name the sources you used, with their labels such as file: notes.md or link: Example.\n\n"
        f"{sources}\n\n"
        f"Question: {question}"
    )
    return complete(prompt)