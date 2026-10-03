from flask import request, jsonify
from app.extensions import db
from app.models.user import User
from app.services.auth import register_user, authenticate_user

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = register_user(data['name'], data['email'], data['password'])
    return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = authenticate_user(data['email'], data['password'])
    return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_password', None)
    session.pop('user_created_at', None)
    session.pop('user_updated_at', None)
    session.pop('user_is_active', None)
    session.pop('user_is_superuser', None)
    return jsonify({'message': 'Logout successful', 'user': None}), 200