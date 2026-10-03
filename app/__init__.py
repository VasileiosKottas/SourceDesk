from flask import Flask
from app.extensions import db

create_app = Flask(__name__)
db.init_app(create_app)