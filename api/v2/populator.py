from flask import Blueprint, jsonify, request
from db.models import TestPatient, User, AssignPatient, NewTestPatient, CallLogs, DischargedPatients  # Updated to use TestPatient instead of Patient
from db.extensions import db
import os, json
from pathlib import Path
from .utils import populate_test_patients_from_excel, updated_data_population
from sqlalchemy import text
from datetime import datetime

populator_api = Blueprint('populator api endpoints', __name__, url_prefix='/api/v2/populator')

@populator_api.route('/', methods=['GET'])
def home():
    return jsonify({"home": "home"})

@populator_api.route('/populate_custom_patient_data', methods=['GET'])
def populate_test_patient_data():
    # Get the absolute path to the test patients JSON file.
    current_dir = Path(__file__).parent
    base_dir = current_dir.parent
    file_path = base_dir / "utils" / "test_patients.json"  # Ensure this file exists and matches the TestPatient fields
    print(f'File Path To Test Patient.json is: {file_path}')
    
    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    try:
        with open(file_path, "r") as file:
            patients = json.load(file)

        # Delete existing test patient records before bulk inserting new ones.
        db.session.execute(db.delete(TestPatient))
        db.session.bulk_insert_mappings(TestPatient, patients)
        db.session.commit()

        return jsonify({"message": "Test patient data populated successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

@populator_api.route('/populate_given_patient_data', methods=["GET"])
def upload_excel():
    try:
        status = updated_data_population()
        print(status)
        return jsonify({
            "message": "Data Populated Successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Error: {e}"
        }), 500

@populator_api.route('/populate_call_logs', methods=['GET'])
def populate_callLogs():
    current_dir = Path(__file__).resolve().parent.parent
    base_dir = current_dir.parent
    file_path = base_dir / "data" / "call_logs.json"

    try:
        with open(file_path, "r") as f:
            call_logs_data = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Error reading file: {str(e)}"}), 500

    for log in call_logs_data:
        try:
            new_log = CallLogs(
                id=log.get("id"),
                patient_id=log.get("patient_id"),
                call_date=datetime.strptime(log.get("call_date"), "%Y-%m-%d").date(),
                call_time=datetime.strptime(log.get("call_time"), "%H:%M:%S").time(),
                admin_comment=log.get("admin_comment")
            )
            db.session.add(new_log)
        except Exception as e:
            return jsonify({"error": f"Error processing log {log}: {str(e)}"}), 500

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database commit error: {str(e)}"}), 500

    return jsonify({"message": "Call logs populated successfully"}), 200

@populator_api.route('/popluate_user_data', methods=['GET'])
def insert_users_orm():
    # Define your user data as a list of dictionaries.
    users_data = [
        {"fname": "Alice", "lname": "Johnson", "email": "alice.johnson@example.com", "password": "password1", "role": "Admin"},
        {"fname": "Bob", "lname": "Smith", "email": "bob.smith@example.com", "password": "password2", "role": "Clinician"},
        {"fname": "Charlie", "lname": "Brown", "email": "charlie.brown@example.com", "password": "password3", "role": "Super User"},
        {"fname": "Diana", "lname": "Prince", "email": "diana.prince@example.com", "password": "password4", "role": "Admin"},
        {"fname": "Ethan", "lname": "Hunt", "email": "ethan.hunt@example.com", "password": "password5", "role": "Clinician"},
        {"fname": "Fiona", "lname": "Shaw", "email": "fiona.shaw@example.com", "password": "password6", "role": "Super User"},
        {"fname": "George", "lname": "Clooney", "email": "george.clooney@example.com", "password": "password7", "role": "Admin"},
        {"fname": "Hannah", "lname": "Montana", "email": "hannah.montana@example.com", "password": "password8", "role": "Clinician"},
        {"fname": "Ivan", "lname": "Drago", "email": "ivan.drago@example.com", "password": "password9", "role": "Super User"},
        {"fname": "Julia", "lname": "Roberts", "email": "julia.roberts@example.com", "password": "password10", "role": "Admin"}
    ]
    try:
        # Option 1: Bulk insert using the ORM
        db.session.bulk_insert_mappings(User, users_data)
        db.session.commit()
        return jsonify({"message": "10 users inserted successfully using ORM!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@populator_api.route('/update_key_codes', methods=['GET'])
def update_key_codes():
    from random import sample
    # Query all rows with key_code "N/A"
    rows = NewTestPatient.query.filter_by(key_code="N/A").all()
    if len(rows) < 18:
        return jsonify({"error": "Not enough rows with key_code 'N/A'"}), 400

    # Randomly select 10 rows and update key_code to "3- Ongoing Procedure"
    first_selection = sample(rows, 10)
    for row in first_selection:
        row.key_code = "3- Ongoing Procedure"

    # Get remaining rows with key_code "N/A"
    remaining = [r for r in rows if r not in first_selection]
    # Randomly select 8 rows from the remaining and update key_code to "4 - Discharged"
    second_selection = sample(remaining, 8)
    for row in second_selection:
        row.key_code = "4 - Discharged"

    db.session.commit()
    return jsonify({"message": "Key codes updated successfully."}), 200

@populator_api.route('/update_assigned_patients_record', methods=['GET'])
def update_assigned_patients_records():
    import random
    from sqlalchemy.orm import load_only

    try:
        # Step 1: Retrieve all patients with key_code "3 - Ongoing Procedure"
        ongoing_patients = NewTestPatient.query.filter_by(key_code="3- Ongoing Procedure").options(load_only(NewTestPatient.id)).all()
        if not ongoing_patients:
            return jsonify({"message": "No patients with '3 - Ongoing Procedure' found"}), 200

        # Extract patient IDs
        patient_ids = [patient.id for patient in ongoing_patients]

        # Step 2: Retrieve all clinicians
        clinicians = User.query.filter_by(role="Clinician").options(load_only(User.id)).all()
        if not clinicians:
            return jsonify({"error": "No clinicians found"}), 404

        # Extract clinician IDs
        clinician_ids = [clinician.id for clinician in clinicians]
        num_clinicians = len(clinician_ids)
        num_patients = len(patient_ids)

        # Step 3: Assign patients to clinicians
        assignments = []

        if num_patients >= num_clinicians:
            # Ensure each clinician gets at least one patient
            for i, clinician_id in enumerate(clinician_ids):
                if i < num_patients:
                    assignments.append((patient_ids[i], clinician_id))

            # Assign remaining patients
            remaining_patients = patient_ids[num_clinicians:]
            for patient_id in remaining_patients:
                assigned_clinician = random.choice(clinician_ids)
                assignments.append((patient_id, assigned_clinician))
        else:
            # More clinicians than patients
            # Assign each patient to a clinician
            for i, patient_id in enumerate(patient_ids):
                assignments.append((patient_id, clinician_ids[i]))

            # Randomly assign remaining clinicians to patients
            remaining_clinicians = clinician_ids[num_patients:]
            for clinician_id in remaining_clinicians:
                assigned_patient = random.choice(patient_ids)
                assignments.append((assigned_patient, clinician_id))

        # Step 4: Insert assignments into the assign_patient table
        for patient_id, clinician_id in assignments:
            assignment_entry = AssignPatient(
                patient_id=patient_id,
                clinician_id=clinician_id
            )
            db.session.add(assignment_entry)

        # Commit all changes
        db.session.commit()

        return jsonify({"message": "Patients assigned to clinicians successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@populator_api.route('/update_discharged_patients', methods=['GET'])
def update_discharged_patients():
    import random 

    try:
        # Step 1: Get all patients with key_code "4 - Discharged"
        discharged_patients = NewTestPatient.query.filter_by(key_code="4 - Discharged").all()
        if not discharged_patients:
            return jsonify({"message": "No discharged patients found"}), 200

        # Extract patient IDs
        patient_ids = [patient.id for patient in discharged_patients]

        # Step 2: Get all clinicians
        clinicians = User.query.filter_by(role="Clinician").all()
        if not clinicians:
            return jsonify({"error": "No clinicians found"}), 404

        # Extract clinician IDs
        clinician_ids = [clinician.id for clinician in clinicians]

        # Step 3: Randomly assign discharged patients to clinicians
        for patient_id in patient_ids:
            assigned_clinician = random.choice(clinician_ids)  # Random clinician assignment

            # Generate random discharge notes and recovery instructions
            discharge_notes = random.choice([
                "Patient has recovered well", 
                "Patient requires further monitoring", 
                "Discharged with mild symptoms"
            ])

            recovery_instructions = random.choice([
                "Follow-up in 2 weeks", 
                "Regular medication required", 
                "No further action needed"
            ])

            # Insert into DischargedPatients table
            discharged_entry = DischargedPatients(
                patient_id=patient_id,
                clinician_id=assigned_clinician,
                discharge_notes=discharge_notes,
                recovery_instructions=recovery_instructions
            )

            db.session.add(discharged_entry)

        # Commit all changes
        db.session.commit()

        return jsonify({"message": "Discharged patients updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    

