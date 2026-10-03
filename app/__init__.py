from flask import Flask
from app.blueprints.auth import auth_bp
from app.blueprints.links import links_bp
from app.config import Config
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(links_bp)
    return app