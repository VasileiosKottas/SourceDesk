import bcrypt
from app.models.user import User
from app.extensions import db

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")   

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

def register_user(name: str, email: str, password: str) -> dict:
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password)
    )
    db.session.add(user)
    db.session.commit()
    return user.to_dict()

def authenticate_user(email: str, password: str) -> dict:
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError('User not found')
    if not verify_password(password, user.password_hash):
        raise ValueError('Invalid password')
    return user.to_dict()
