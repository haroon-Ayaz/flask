from flask import Blueprint, jsonify, request
from db.models import Patient, User  # Modified import path
from db.extensions import db
import os, json
from pathlib import Path

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/home')
def get_home():
    return jsonify({"message": "welcome from home"})

@api_bp.route('/getdata', methods=['GET'])
def get_data():
    try:
        patients = Patient.query.all()
        patient_list = [
            {
                "id": patient.id,
                "rxkid": patient.rxkid,
                "title": patient.title,
                "fname": patient.fname,
                "lname": patient.lname,
                "address": patient.address,
                "postcode": patient.postcode,
                "phone_number": patient.phone_number,
                "home_number": patient.home_number,
                "problem": patient.problem,
                "assignto": patient.assigned_to,
                "status": patient.status,
            }
            for patient in patients
        ]
        return jsonify(patient_list), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@api_bp.route('/get_waiting_patients', methods=['GET'])
def get_waiting_patients():
    try:
        waiting_patients = Patient.query.filter_by(status="Waiting").all()
        patient_list = [{
                "id": patient.id,
                "rxkid": patient.rxkid,
                "title": patient.title,
                "fname": patient.fname,
                "lname": patient.lname,
                "address": patient.address,
                "postcode": patient.postcode,
                "phone_number": patient.phone_number,
                "home_number": patient.home_number,
                "problem": patient.problem,
                "assigned_to": patient.assigned_to,
                "status": patient.status,
            }
            for patient in waiting_patients
        ]
        return jsonify(patient_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/get_procedure_patients', methods=['GET'])
def get_procedure_patients():
    try:
        waiting_patients = Patient.query.filter_by(status="Procedure").all()
        patient_list = [{
                "id": patient.id,
                "rxkid": patient.rxkid,
                "title": patient.title,
                "fname": patient.fname,
                "lname": patient.lname,
                "address": patient.address,
                "postcode": patient.postcode,
                "phone_number": patient.phone_number,
                "home_number": patient.home_number,
                "problem": patient.problem,
                "assigned_to": patient.assigned_to,
                "status": patient.status,
            }
            for patient in waiting_patients
        ]
        return jsonify(patient_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/get_discharged_patients', methods=['GET'])
def get_discharged_patients():
    try:
        waiting_patients = Patient.query.filter_by(status="Discharged").all()
        patient_list = [{
            "id": patient.id,
            "rxkid": patient.rxkid,
            "title": patient.title,
            "fname": patient.fname,
            "lname": patient.lname,
            "address": patient.address,
            "postcode": patient.postcode,
            "phone_number": patient.phone_number,
            "home_number": patient.home_number,
            "problem": patient.problem,
            "assigned_to": patient.assigned_to,
            "status": patient.status,
        }
            for patient in waiting_patients
        ]
        return jsonify(patient_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/populate_patient_data', methods=['GET'])
def populatedata():
    # Get the absolute path of the current file
    current_dir = Path(__file__).parent
    # Go up one level to reach flask-mvp directory
    base_dir = current_dir.parent
    file_path = base_dir / "utils" / "patients.json"

    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    try:
        with open(file_path, "r") as file:
            patients = json.load(file)

        db.session.execute(db.delete(Patient))

        db.session.bulk_insert_mappings(Patient, patients)
        db.session.commit()

        return jsonify({"message": "Patients data populated successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

@api_bp.route('/popluate_user_data', methods=['GET'])
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

@api_bp.route('/addpatient', methods=['POST'])
def add_patient():
    data = request.get_json()

    rxkid = data.get('rxkid')
    title = data.get('title')
    fname = data.get('fname')
    lname = data.get('sname')
    address = data.get('address')
    postal_code = data.get('postcode')
    mobile_number = data.get('mobilephone')
    home_phone_number = data.get('homephone')
    problem = data.get('problem')

    new_patient = Patient(
        rxkid=rxkid,
        title=title,
        fname=fname,
        lname=lname,
        address=address,
        postcode=postal_code,
        phone_number=mobile_number,
        home_number=home_phone_number,
        problem=problem,
        assigned_to="None",
        status="waiting",
    )

    db.session.add(new_patient)
    db.session.commit()

    return jsonify({"message": "Patient added successfully!"}), 201

@api_bp.route('/assignpatient', methods=['POST'])
def assign_patient():
    try:
        data = request.get_json()
        patient_id = data.get("patient_id")
        clinician_name = data.get("assigned_to")

        print(f'patient_id: {patient_id}')
        print(f'clinician_name: {clinician_name}')

        if not patient_id or not clinician_name:
            return jsonify({"error": "Patient ID and clinician name are required"}), 400

        # Find patient by ID
        patient = Patient.query.filter_by(rxkid=patient_id).first()

        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Update patient details
        patient.status = "Procedure"
        patient.assigned_to = clinician_name

        db.session.add(patient)  # Ensure SQLAlchemy tracks the change
        db.session.commit()

        return jsonify({"message": "Patient assigned successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/discharge_patient', methods=['POST'])
def discharge_patient():
    data = request.get_json()
    patient_id = data.get("patient_id")

    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400

    patient = Patient.query.filter_by(rxkid=patient_id).first()

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    # Update the patient's status and assigned_to fields
    patient.status = "Discharged"
    patient.assigned_to = None  # Assuming None is acceptable for the assigned_to field

    db.session.add(patient)  # Ensure SQLAlchemy tracks the change
    db.session.commit()

    return jsonify({"message": "Patient discharged successfully"}), 200

@api_bp.route('/get_statistics', methods=['GET'])
def get_statistics():
    try:
        total_waiting = Patient.query.filter_by(status="Waiting").count()
        total_procedures = Patient.query.filter_by(status="Procedure").count()
        total_discharged = Patient.query.filter_by(status="Discharged").count()

        return jsonify({
            "total_waiting": total_waiting,
            "total_procedures": total_procedures,
            "total_discharged": total_discharged
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/send_sms', methods=['POST'])
def send_sms():
    """Send an SMS notification using the GOV.UK Notify API."""

    # Extract JSON data from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request, no JSON payload received"}), 400

    recipient_number = data.get("recipient_number")
    appointment_date = data.get("date")

    print(f'Recipient number: {recipient_number}')
    print(f'Appointment date: {appointment_date}')

    # Configuration
    API_KEY = "adalovelace-8413bf9f-5a51-4f58-a46c-fc4eb185fe50-949fb1be-bc38-49e2-a668-45c3157d59ed"
    TEMPLATE_ID = "a6e1a749-f102-45ea-979e-5a21586275f5"

    # Initialize the API client
    try:
        from notifications_python_client.notifications import NotificationsAPIClient
        client = NotificationsAPIClient(API_KEY)
    except Exception as e:
        return jsonify({"error": "Failed to initialize Notify API client", "details": str(e)}), 500

    # Attempt to send SMS notification
    try:
        response = client.send_sms_notification(
            phone_number=recipient_number,
            template_id=TEMPLATE_ID,
            personalisation={"date": appointment_date},
            reference="appointment_reminder"
        )

        return jsonify({
            "message": "SMS sent successfully!",
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to send SMS notification",
            "details": str(e)
        }), 500

@api_bp.route('/get_clinicians', methods=['GET'])
def get_clinicians():
    try:
        clinicians = User.query.filter_by(role="Clinician").all()
        clinician_list = [{"id": c.id, "fname": c.fname, "lname": c.lname, "email": c.email} for c in clinicians]
        total_clinicians = len(clinicians)

        return jsonify({
            "total_clinicians": total_clinicians,
            "clinicians": clinician_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
