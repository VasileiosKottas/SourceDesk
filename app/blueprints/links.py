from flask import Blueprint, jsonify, request, session

from app.extensions import db
from app.services.links import create_link, list_links

links_bp = Blueprint("links", __name__)


@links_bp.post("/links")
def create_link_route():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401

    data = request.get_json(silent=True) or {}
    try:
        link = create_link(user_id, data.get("url"), data.get("title"), data.get("notes"))
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Link created successfully", "link": link}), 201


@links_bp.get("/links")
def list_links_route():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"message": "Login required"}), 401

    try:
        links = list_links(user_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Links listed successfully", "links": links}), 200
