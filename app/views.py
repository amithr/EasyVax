from app import app, db
from flask import render_template, request, redirect, url_for, jsonify, session, flash
from app.models import Doctor, Patient, Vaccine_Dose
from fpdf import FPDF
import qrcode
import os
import smtplib, ssl
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def send_doctor_registration_email(doctor_id):
    if not doctor_id:
        flash("Error sending confirmation email.")
        return redirect(url_for('index'))
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    if doctor:


        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email="boorsokkaimak@gmail.com"
        password = "Sulochana2493!"

        message = MIMEMultipart("alternative")
        message["Subject"] = "EasyVax Confirmation Email"
        message["From"] = sender_email
        message["To"] = doctor.email

        confirmation_url = url_for('confirm_doctor_registration', doctor_id=doctor.id, _external=True)

        #HTML Message Part
        html = "\
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

        message_text = MIMEText(html, "html")
        message.attach(message_text)

        context = ssl.create_default_context()

        try:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, doctor.email, message.as_string())
        except Exception as e:
            print(e)
        finally:
            server.quit()
    return

@app.route('/')
def index():
    send_doctor_registration_email(1)
    if 'doctor' in session.keys():
        return redirect(url_for('patients'))
    return render_template('main.html')

@app.route('/register-doctor', methods=['POST'])
def register_doctor():

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

@app.route('/validate-doctor-registration', methods=['POST'])
def validate_doctor_registration():
    if request.method == "POST":
        email_address = request.get_json()['email']
        doctor = Doctor.query.filter_by(email=email_address).first()
        if doctor:
            return jsonify({"user_exists": "true"})
        else:
            return jsonify({"user_exists": "false"})


@app.route('/login-doctor', methods=['POST'])
def login_doctor():
    form = request.form
    doctor = Doctor.query.filter_by(email=form['email-address']).first()
    if not doctor:
        flash("Doctor doesn't exist")
        return redirect(url_for('index'))
    if doctor.check_password(form['password']):
        session['doctor'] = doctor.id
        return redirect(url_for('patients'))
    else:
        flash('Password was incorrect')
        return redirect(url_for('index'))


@app.route('/logout-doctor', methods=['POST', 'GET'])
def logout_doctor():
    session.pop('doctor', None)
    return redirect(url_for('index'))


@app.route('/confirm-registration/<doctor_id>', methods=['GET'])
def confirm_doctor_registration(doctor_id):
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
        

@app.route('/patients', methods=['POST', 'GET'])
def patients():
    doctor_id = None
    if session['doctor']:
        doctor_id = session['doctor']
        patients = Patient.query.filter_by(doctor_id=doctor_id)
        return render_template('patients.html', patients=patients)
    return render_template('patients.html')

@app.route('/register-patient', methods=['POST'])
def register_patient():
    form = request.form
    email = form['email-address']
    patient = Patient.query.filter_by(email=email).first()
    if not patient:
        patient = Patient(
            name = form['name'],
            email=email,
            phone_number = form['phone-number'],
            doctor_id = session['doctor']
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient successfully registered')
        return redirect(url_for('patients'))
    else:
        flash('Patient already exists')
        return redirect(url_for('patients'))

@app.route('/vaccine-record/<patient_id>', methods=['GET', 'POST'])
def vaccine_record(patient_id):
    if not patient_id:
        return redirect(url_for('patients'))
    patient = Patient.query.filter_by(id=patient_id).first()
    if patient:
        vaccine_doses = Vaccine_Dose.query.filter_by(patient_id=patient_id)
        return render_template('vaccine_record.html', vaccine_doses=vaccine_doses, patient_id=patient_id)

@app.route('/add-vaccine-record/<patient_id>', methods=['POST', 'GET'])
def add_vaccine_record(patient_id):
    form = request.form
    dose_id = form['dose-id']
    dose_number = form['dose-number']
    vaccine_dose = Vaccine_Dose.query.filter_by(patient_id=patient_id, dose_no=dose_number).first()
    if vaccine_dose:
        flash("This dose number has already been entered.")
        return redirect(url_for('vaccine_record', patient_id=patient_id))
    vaccine_dose = Vaccine_Dose.query.filter_by(dose_id=dose_id).first()
    if vaccine_dose:
        flash("A dose with this serial number already exists in the database.")
        return redirect(url_for('vaccine_record', patient_id=patient_id))
    vaccine_dose = Vaccine_Dose(
        type=form['type'],
        volume = form['volume'],
        dose_no=form['dose-number'],
        dose_id=dose_id,
        patient_id=patient_id
    )
    db.session.add(vaccine_dose)
    db.session.commit()
    flash('Vaccine dose successfully added.')
    return redirect(url_for('vaccine_record', patient_id=patient_id))


@app.route('/delete-vaccine-record/<patient_id>/<vaccine_id>', methods=['GET'])
def delete_vaccine_record(patient_id, vaccine_id):
    Vaccine_Dose.query.filter_by(id=vaccine_id).delete()
    db.session.commit()
    flash('Vaccine dose successfully deleted.')
    return redirect(url_for('vaccine_record', patient_id=patient_id))


def generate_qr_code(verification_path, patient_id):
    qr = qrcode.QRCode(
        version=1,
        box_size = 10,
        border = 5
    )
    qr.add_data(verification_path)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    file_name = "qr_code-" + str(patient_id) + ".png"
    path = os.path.join("app/static", file_name)
    img.save(path)
    return path



def generate_pdf(patient):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    name_string = "Name: " + patient.name
    id_string = "Patient ID: " + str(patient.id)
    email_address_string = "Email Address: " + patient.email
    doctor_id_string = "Doctor ID: " + str(patient.doctor_id)
    pdf.cell(40, 10, name_string, ln=2, align="L")
    pdf.cell(40, 10, id_string, ln=2, align="L")
    pdf.cell(40, 10, email_address_string, ln=2, align="L")
    pdf.cell(40, 10, doctor_id_string, ln=2, align="L")
    verification_path = url_for('verify_vaccination_status', patient_id = patient.id, _external=True)
    img_path = generate_qr_code(verification_path, patient.id)
    pdf.cell(40, 10, "Scan QR code to verify:")
    pdf.image(img_path, x=50, y=100)
    pdf.output('vaccine_passport.pdf', 'F')
    return True



@app.route('/generate-certificate/<patient_id>', methods=['GET'])
def generate_certificate(patient_id):
    if not patient_id:
        return redirect(url_for('patients'))
    patient = Patient.query.filter_by(id=patient_id).first()
    if patient:
        generate_pdf(patient)
        flash("Certificate generated")
        return redirect(url_for('patients'))
    else:
        flash("Error generating certificate")
        return redirect(url_for('patients'))

@app.route('/verify-vaccination-status/<patient_id>', methods=['GET'])
def verify_vaccination_status(patient_id):
    if not patient_id:
        return redirect(url_for('patients'))
    patient = Patient.query.filter_by(id=patient_id).first()
    if patient:
        if (len(patient.vaccine_doses) >= 2):
            return "Fully Vaccinated"
        else:
            return "Not Fully Vaccinated"