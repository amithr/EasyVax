from app import db
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Patient
from fpdf import FPDF
import qrcode, os

patient = Blueprint('patient', __name__, url_prefix='/patient')

@patient.route('/patients-dashboard', methods=['POST', 'GET'])
def display_patients():
    doctor_id = None
    if session['doctor']:
        doctor_id = session['doctor']
        patients = Patient.query.filter_by(doctor_id=doctor_id)
        return render_template('patients.html', patients=patients)
    return render_template('patients.html')

@patient.route('/register', methods=['POST'])
def register():
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
        return redirect(url_for('patient.display_patients'))
    else:
        flash('Patient already exists')
        return redirect(url_for('patient.display_patients'))

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
    verification_path = url_for('patient.verify_vaccination_status', patient_id = patient.id, _external=True)
    img_path = generate_qr_code(verification_path, patient.id)
    pdf.cell(40, 10, "Scan QR code to verify:")
    pdf.image(img_path, x=50, y=100)
    pdf.output('vaccine_passport.pdf', 'F')
    return True



@patient.route('/generate-certificate/<patient_id>', methods=['GET'])
def generate_certificate(patient_id):
    if not patient_id:
        return redirect(url_for('patient.display_patients'))
    patient = Patient.query.filter_by(id=patient_id).first()
    if patient:
        generate_pdf(patient)
        flash("Certificate generated")
        return redirect(url_for('patient.display_patients'))
    else:
        flash("Error generating certificate")
        return redirect(url_for('patient.display_patients'))

@patient.route('/verify-vaccination-status/<patient_id>', methods=['GET'])
def verify_vaccination_status(patient_id):
    if not patient_id:
        return redirect(url_for('patient.display_patients'))
    patient = Patient.query.filter_by(id=patient_id).first()
    if patient:
        if (len(patient.vaccine_doses) >= 2):
            return "Fully Vaccinated"
        else:
            return "Not Fully Vaccinated"