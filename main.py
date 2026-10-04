from wsgi import app

with app.app_context():
    print("Database tables created successfully")
