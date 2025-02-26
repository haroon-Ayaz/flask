from flask import Blueprint, jsonify, request
from db.models import TestPatient, User, Patient, NewTestPatient, CallLogs  # Updated to use TestPatient instead of Patient
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
