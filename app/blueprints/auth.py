from flask import request, jsonify
from flask import Blueprint
from app.extensions import db
from app.models.user import User
from app.services.auth import register_user, authenticate_user
from flask import Blueprint, request, jsonify, session

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        user = register_user(data['name'], data['email'], data['password'])
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify({'message': 'User registered successfully', 'user': user}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        user = authenticate_user(data['email'], data['password'])
        session["user_id"] = user["id"]
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify({'message': 'Login successful', 'user': user}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful', 'user': None}), 200