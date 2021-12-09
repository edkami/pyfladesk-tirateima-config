from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///DBTirateima.db"
app.config['SECRET_KEY'] = "PASLFASDKFASDFAS"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./app/static/client-img-folder"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.models import banco_dados
from app.models.banco_dados import init_db

if app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///DBTirateima.db":
    # Use memory SQLITE database! Meaning the HDD is never touched!
    # Since this database will be in the memory, we have to create
    # it at the beginning of every app run.
    init_db()

from app.controllers import default