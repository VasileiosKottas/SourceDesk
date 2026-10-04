from flask import Blueprint, jsonify, request, session

from app.services.files import list_files, save_file, get_file

files_bp = Blueprint("files", __name__)


@files_bp.post("/files")
def create_file_route():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401

    upload = request.files.get("file")
    if upload is None or not upload.filename:
        return jsonify({"message": "A file is required"}), 400

    try:
        record = save_file(user_id, upload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "File saved successfully", "file": record}), 201


@files_bp.get("/files")
def list_files_route():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401

    try:
        records = list_files(user_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Files listed successfully", "files": records}), 200

@files_bp.get("/files/<int:file_id>")
def get_file_route(file_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401
    
    try:
        record = get_file(user_id, file_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if record is None:
        return jsonify({"message": "File not found"}), 404
    return jsonify({"message": "File retrieved successfully", "file": record}), 200
