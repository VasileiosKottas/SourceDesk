from app.models.user import User

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(
        name=data['name'],
        email=data['email'],
        password=hash_password(data['password'])
    )
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not verify_password(data['password'], user.password):
        return jsonify({'message': 'Invalid password'}), 401
    return jsonify({'message': 'Login successful'}), 200

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
    return jsonify({'message': 'Logout successful'}), 200