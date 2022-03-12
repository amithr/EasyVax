from app import db
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from app.models import Vaccine_Dose, Patient


vaccine_dose = Blueprint('vaccine_dose', __name__, url_prefix='/vaccine-dose')

@vaccine_dose.route('/vaccine-record/<patient_id>', methods=['GET', 'POST'])
def display_records(patient_id):
    if not patient_id:
        return redirect(url_for('patients'))
    patient = Patient.query.filter_by(id=patient_id).first()
    if patient:
        vaccine_doses = Vaccine_Dose.query.filter_by(patient_id=patient_id)
        return render_template('vaccine_record.html', vaccine_doses=vaccine_doses, patient_id=patient_id)

@vaccine_dose.route('/add-vaccine-record/<patient_id>', methods=['POST', 'GET'])
def add_record(patient_id):
    form = request.form
    dose_id = form['dose-id']
    dose_number = form['dose-number']
    vaccine_dose = Vaccine_Dose.query.filter_by(patient_id=patient_id, dose_no=dose_number).first()
    if vaccine_dose:
        flash("This dose number has already been entered.")
        return redirect(url_for('vaccine_dose.display_records', patient_id=patient_id))
    vaccine_dose = Vaccine_Dose.query.filter_by(dose_id=dose_id).first()
    if vaccine_dose:
        flash("A dose with this serial number already exists in the database.")
        return redirect(url_for('vaccine_dose.display_records', patient_id=patient_id))
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
    return redirect(url_for('vaccine_dose.display_records', patient_id=patient_id))


@vaccine_dose.route('/delete-record/<patient_id>/<vaccine_id>', methods=['GET'])
def delete_record(patient_id, vaccine_id):
    Vaccine_Dose.query.filter_by(id=vaccine_id).delete()
    db.session.commit()
    flash('Vaccine dose successfully deleted.')
    return redirect(url_for('vaccine_dose.display_records', patient_id=patient_id))

