from flask import Blueprint, jsonify, request
from db.models import TestPatient, User, Patient  # Updated to use TestPatient instead of Patient
from db.extensions import db
import os, json
from pathlib import Path
from .utils import populate_test_patients_from_excel

v2_api_bp = Blueprint('v2/api', __name__, url_prefix='/api/v2/')

@v2_api_bp.route('/home')
def get_home():
    return jsonify({"message": "welcome from home"})

@v2_api_bp.route('/get_test_patients', methods=['GET'])
def get_test_patients():
    try:
        test_patients = TestPatient.query.all()
        patient_list = [
            {
                "id": tp.id,
                "rxkid": tp.rxkid,
                "reporting_status": tp.reporting_status,
                "test_type_main": tp.test_type_main,
                "test_type": tp.test_type,
                "waitlist_name": tp.waitlist_name,
                "unit_no": tp.unit_no,
                "surname": tp.surname,
                "forename": tp.forename,
                "points": tp.points,
                "requires_pre_add": tp.requires_pre_add,
                "key_code": tp.key_code,
                "comment": tp.comment,
                "dated": tp.dated,
                "sub_type": tp.sub_type,
                "referral_priority": tp.referral_priority,
                "date_added_to_wl": tp.date_added_to_wl,
                "adj_wl_start": tp.adj_wl_start,
                "waitlist_name_2": tp.waitlist_name_2,
                "remvl_dttm": tp.remvl_dttm,
                "weeks_wait": tp.weeks_wait,
                "current_rtt_waits": tp.current_rtt_waits,
                "indication": tp.indication,
                "appointment_date": tp.appointment_date,
                "appt_by_date_ipm": tp.appt_by_date_ipm,
                "appt_by_date_calculated": tp.appt_by_date_calculated,
                "short_notice_flag": tp.short_notice_flag,
            }
            for tp in test_patients
        ]
        return jsonify(patient_list), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@v2_api_bp.route('/populate_test_patient_data', methods=['GET'])
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

@v2_api_bp.route('/upload_excel', methods=["GET"])
def upload_excel():
    current_dir = Path(__file__).resolve().parent
    base_dir = current_dir.parent
    file_path = base_dir / "data" / "data.xlsx"
    try:
        populate_test_patients_from_excel(filepath=file_path)
        return jsonify({
            "message": "Data Populated Successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Error: {e}"
        }), 500

@v2_api_bp.route('/populate_user_data', methods=['GET'])
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
        db.session.bulk_insert_mappings(User, users_data)
        db.session.commit()
        return jsonify({"message": "10 users inserted successfully using ORM!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@v2_api_bp.route('/send_sms', methods=['POST'])
def send_sms():
    """Send an SMS notification using the GOV.UK Notify API."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request, no JSON payload received"}), 400

    recipient_number = data.get("recipient_number")
    appointment_date = data.get("date")

    print(f'Recipient number: {recipient_number}')
    print(f'Appointment date: {appointment_date}')

    API_KEY = "adalovelace-8413bf9f-5a51-4f58-a46c-fc4eb185fe50-949fb1be-bc38-49e2-a668-45c3157d59ed"
    TEMPLATE_ID = "a6e1a749-f102-45ea-979e-5a21586275f5"

    try:
        from notifications_python_client.notifications import NotificationsAPIClient
        client = NotificationsAPIClient(API_KEY)
    except Exception as e:
        return jsonify({"error": "Failed to initialize Notify API client", "details": str(e)}), 500

    try:
        response = client.send_sms_notification(
            phone_number=recipient_number,
            template_id=TEMPLATE_ID,
            personalisation={"date": appointment_date},
            reference="appointment_reminder"
        )
        return jsonify({"message": "SMS sent successfully!"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to send SMS notification", "details": str(e)}), 500

@v2_api_bp.route('/get_clinicians', methods=['GET'])
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

@v2_api_bp.route('/get_statistics', methods=['GET'])
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


