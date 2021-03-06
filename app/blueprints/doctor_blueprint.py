from app import db
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from app.models import Doctor
from app.utilities.emails import send_email

doctor = Blueprint('doctor', __name__, url_prefix='/doctor')


def send_doctor_registration_email(doctor_id):
    if not doctor_id:
        flash("Error sending confirmation email.", category="error")
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

    doctor = Doctor.query.filter_by(email=form['email-address']).first()
    if doctor:
        flash("Enter a unique email address.", category="error")
        return redirect(url_for('index'))

    doctor = Doctor.query.filter_by(email=form['phone-number']).first()
    if doctor:
        flash("Enter a unique phone number.", category="error")
        return redirect(url_for('index'))

    doctor = Doctor.query.filter_by(email=form['government-id']).first()
    if doctor:
        flash("Enter a unique phone government id.", category="error")
        return redirect(url_for('index'))

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
    flash("Confirmation email sent.", category="success")
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
        flash("Doctor doesn't exist.", category="error")
        return redirect(url_for('index'))
    if doctor.check_password(form['password']):
        session['doctor'] = doctor.id
        return redirect(url_for('patient.display_patients'))
    else:
        flash("Password was incorrect.", category="error")
        return redirect(url_for('index'))


@doctor.route('/logout-doctor', methods=['POST', 'GET'])
def logout():
    session.pop('doctor', None)
    return redirect(url_for('index'))


@doctor.route('/confirm-registration/<doctor_id>', methods=['GET'])
def confirm_registration(doctor_id):
    if not doctor_id:
        flash("Error confirming registration.", category="error")
        return redirect(url_for('index'))
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    if doctor:
        doctor.is_confirmed=True
        db.session.add(doctor)
        db.session.commit()
        flash("Registration confirmed.", category="success")
    else:
        flash("Error confirming registration.", category="error")
    return redirect(url_for('index'))

@doctor.route('/initiate-password-change', methods=['GET'])
def initiate_password_change():
    return render_template('forgot_your_password.html')


def handle_sending_password_change_email(doctor):
    password_change_url = url_for('doctor.display_change_password_form', doctor_id=doctor.id, _external=True)
    html_message = "\
        <html> \
        <body> \
            <p><b>Hello " + doctor.name + "</b>, \
            <br/> \
            Please click below to enter a new password.<br> \
            Click <a href=" + password_change_url + ">here</a>.  \
            </p> \
        </body> \
        </html> \
        "
    send_email("Password Change Request", html_message, doctor.email)
    return

@doctor.route('/send-password-change-email', methods=['POST'])
def send_password_change_email():
    form = request.form
    doctor = Doctor.query.filter_by(email=form['email-address']).first()
    if doctor:
        handle_sending_password_change_email(doctor)
        flash("An email has been sent with instructions on how to create a new password.", category="success")
    else:
        flash("A user with this email does not exist.", category="error")
    return redirect(url_for('index'))

@doctor.route('/change-password-form/<doctor_id>', methods=['GET'])
def display_change_password_form(doctor_id):
    return render_template('change_password.html', doctor_id=doctor_id)

@doctor.route('/change-password/<doctor_id>', methods=['POST'])
def change_password(doctor_id):
    form = request.form
    if not form['password'] == form['password']:
        flash("Passwords do not match.", category="error")
        return redirect(url_for('index'))
    if doctor_id:
        doctor = Doctor.query.filter_by(id=doctor_id).first()
        doctor.set_password(form['password'])
        db.session.add(doctor)
        db.session.commit()
        flash("Passwords successfully changed, please login using new password.", category="error")
    else:
        flash("Invalid doctor ID.")
    return redirect(url_for('index'))

