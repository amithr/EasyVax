from app import app
from flask import render_template, redirect, url_for, session


@app.route('/')
def index():
    if 'doctor' in session.keys():
        return redirect(url_for('patient.display_patients'))
    return render_template('main.html')
        

