from flask import Flask
from sqlalchemy import inspect, text

from app.blueprints.auth import auth_bp
from app.blueprints.files import files_bp
from app.blueprints.links import links_bp
from app.config import Config
from app.extensions import db


def ensure_content_columns():
    inspector = inspect(db.engine)
    for table in ("files", "links"):
        if not inspector.has_table(table):
            continue
        names = {column["name"] for column in inspector.get_columns(table)}
        if "content_text" not in names:
            db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN content_text TEXT"))
        if "content_error" not in names:
            db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN content_error TEXT"))
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(links_bp)
    app.register_blueprint(files_bp)
    with app.app_context():
        db.create_all()
        ensure_content_columns()
    return app