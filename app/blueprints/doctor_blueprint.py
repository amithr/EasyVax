from app import db
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from app.models import Doctor
from utilities.email import send_email

doctor = Blueprint('doctor', __name__, url_prefix='/doctor')


def send_doctor_registration_email(doctor_id):
    if not doctor_id:
        flash("Error sending confirmation email.")
        return redirect(url_for('index'))
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    if doctor:
        confirmation_url = url_for('doctor.confirm_registration', doctor_id=doctor.id, _external=True)

        #HTML Message Part
        html_message = "\
        <html> \
        <body> \
            <p><b>Hello " + doctor.name + "</b>, \
            <br/> \
            Please click below to confirm your registration with EasyVax as a doctor.<br> \
            Click <a href=" + confirmation_url + ">here</a>.  \
            </p> \
        </body> \
        </html> \
        "

        send_email("Confirm EasyVax Registration", html_message, doctor.email)
    return True

@doctor.route('/register', methods=['POST'])
def register():

    form = request.form
    doctor = Doctor(
        name=form['name'],
        email=form['email-address'],
        phone_number=form['phone-number'],
        government_id=form['government-id']
    )
    doctor.set_password(form['password'])
    db.session.add(doctor)
    db.session.commit()
    send_doctor_registration_email(doctor.id)
    flash("Confirmation email sent.")
    return redirect(url_for('index'))

@doctor.route('/validate-registration', methods=['POST'])
def validate_registration():
    if request.method == "POST":
        email_address = request.get_json()['email']
        doctor = Doctor.query.filter_by(email=email_address).first()
        if doctor:
            return jsonify({"user_exists": "true"})
        else:
            return jsonify({"user_exists": "false"})


@doctor.route('/login-doctor', methods=['POST'])
def login():
    form = request.form
    doctor = Doctor.query.filter_by(email=form['email-address']).first()
    if not doctor:
        flash("Doctor doesn't exist")
        return redirect(url_for('index'))
    if doctor.check_password(form['password']):
        session['doctor'] = doctor.id
        return redirect(url_for('patient.display_patients'))
    else:
        flash('Password was incorrect')
        return redirect(url_for('index'))


@doctor.route('/logout-doctor', methods=['POST', 'GET'])
def logout():
    session.pop('doctor', None)
    return redirect(url_for('index'))


@doctor.route('/confirm-registration/<doctor_id>', methods=['GET'])
def confirm_registration(doctor_id):
    if not doctor_id:
        flash("Error confirming registration.")
        return redirect(url_for('index'))
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    if doctor:
        doctor.is_confirmed=True
        db.session.add(doctor)
        db.session.commit()
        flash("Registration confirmed.")
    else:
        flash("Error confirming registration.")
    return redirect(url_for('index'))