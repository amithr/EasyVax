from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__, instance_relative_config=True)

app.config["SECRET_KEY"] = '571ebf8e12ca209536c'
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')  or "postgresql://"+os.getenv("DB_USER") + ":" + os.getenv("DB_PASSWORD") + "@localhost/easyvax"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config.from_object('config')

from app import views
from app import models

from app.blueprints.doctor_blueprint import doctor
from app.blueprints.patient_blueprint import patient
from app.blueprints.vaccine_dose_blueprint import vaccine_dose


app.register_blueprint(doctor)
app.register_blueprint(patient)
app.register_blueprint(vaccine_dose)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

