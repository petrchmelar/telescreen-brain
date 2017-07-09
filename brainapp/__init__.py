from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from brainapp.models import db

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

db.init_app(app)

migrate = Migrate(app, db)