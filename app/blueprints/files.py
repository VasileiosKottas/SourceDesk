import io

from flask import Blueprint, jsonify, request, send_file, session

from app.services.files import (
    delete_file,
    get_file,
    list_files,
    pdf_page_count,
    render_pdf_page,
    save_file,
)

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

@files_bp.delete("/files/<int:file_id>")
def delete_file_route(file_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401
    try:
        deleted = delete_file(user_id, file_id)
        if not deleted:
            return jsonify({"message": "File not found"}), 404
        return jsonify({"message": "File deleted successfully"}), 200
    except Exception:
        return jsonify({"error": "Failed to delete file"}), 500

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

@files_bp.get("/files/<int:file_id>/pages")
def list_pdf_pages_route(file_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401
    try:
        count = pdf_page_count(user_id, file_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if count is None:
        return jsonify({"message": "File not found"}), 404
    return jsonify({"count": count}), 200


@files_bp.get("/files/<int:file_id>/pages/<int:page>")
def get_pdf_page_route(file_id, page):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401
    try:
        image = render_pdf_page(user_id, file_id, page)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if image is None:
        return jsonify({"message": "Page not found"}), 404
    return send_file(io.BytesIO(image), mimetype="image/png")