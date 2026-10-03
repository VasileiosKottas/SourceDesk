from wsgi import app
from app.extensions import db

with app.app_context():
    db.create_all()
    
    print("Database tables created successfully")
    print("Links table created successfully")