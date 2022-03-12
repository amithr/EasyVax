from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, instance_relative_config=True)

app.config["SECRET_KEY"] = '571ebf8e12ca209536c'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///doctor_patient_information.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.config.from_object('config')

from app import views
from app import models
from app.blueprints.doctor_blueprint import doctor
from app.blueprints.patient_blueprint import patient
from app.blueprints.vaccine_dose_blueprint import vaccine_dose


app.register_blueprint(doctor)
app.register_blueprint(patient)
app.register_blueprint(vaccine_dose)

