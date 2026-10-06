from flask import Blueprint, jsonify, request, session

from app.services.questions import (
    ask_model,
    create_question,
    list_questions,
    readable_sources,
    save_asked_question,
    delete_question
)

questions_bp = Blueprint("questions", __name__)


def source_label(source):
    if "file_name" in source:
        return "file", f"file: {source['file_name']}"
    return "link", f"link: {source['title']}"


@questions_bp.post("/questions")
def create_question_route():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401

    data = request.get_json(silent=True) or {}
    question = data.get("question")
    if not question:
        return jsonify({"message": "Question is required"}), 400

    try:
        record = create_question(user_id, question)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Question created successfully", "question": record}), 201

@questions_bp.delete("/questions/<int:question_id>")
def delete_question_route(question_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401
    
    deleted = delete_question(user_id, question_id)
    if not deleted:
        return jsonify({"message": "Question not found"}), 404

    return jsonify({"message": "Question deleted successfully"}), 200

@questions_bp.get("/questions")
def list_questions_route():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401

    try:
        questions = list_questions(user_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Questions listed successfully", "questions": questions}), 200


@questions_bp.post("/ask-question")
def ask_question_route():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401

    data = request.get_json(silent=True) or {}
    question = data.get("question")
    if not question:
        return jsonify({"message": "Question is required"}), 400

    sources = readable_sources(user_id)
    if not sources:
        return jsonify({"message": "No readable sources found"}), 400

    blocks = []
    labels = []
    for source in sources:
        kind, label = source_label(source)
        labels.append({"id": source["id"], "kind": kind, "label": label})
        blocks.append(f"{label}\n{source['content_text']}")

    try:
        answer = ask_model(question, blocks)
        record = save_asked_question(user_id, question, answer, labels)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Question asked successfully",
        "answer": answer,
        "sources": sources,
        "labels": labels,
        "question": record,
    }), 200
