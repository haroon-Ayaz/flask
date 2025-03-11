from flask import Blueprint, jsonify, request
from db.models import TestPatient, User, Patient, NewTestPatient, CallLogs, AssignPatient , DischargedPatients# Updated to use TestPatient instead of Patient
from db.extensions import db
import os, json
from pathlib import Path
from .utils import populate_test_patients_from_excel, updated_data_population
from sqlalchemy import Text, func, text
from datetime import datetime

v2_api_bp = Blueprint('v2/api', __name__, url_prefix='/api/v2/')

@v2_api_bp.route('/home')
def get_home():
    return jsonify({"message": "welcome from home"})

@v2_api_bp.route('/update_comments', methods=['POST'])
def update_patients_comments():
    data = request.get_json()
    
    if not data:
        return jsonify({"Error": "Invalid request, no JSON payload received"}), 400

    patient_id = data["patientId"]
    patient_comment = data["comment"]

    # Look for the patient in NewTestPatient by rxkid
    patient = NewTestPatient.query.filter_by(rxkid=patient_id).first()
    if not patient:
        return jsonify({"Error": "Patient not found"}), 404
    
    print(f"The Newly Formatted Comment Is:\n{patient_comment}")

    # Append the new comment with a newline
    if patient.comment and patient.comment != "N/A":
        patient.comment = patient.comment + "\n" + patient_comment
    else:
        patient.comment = patient_comment

    try:
        db.session.commit()
        return jsonify({"message": "Comments updated successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": f"Failed to update comments: {str(e)}"}), 500

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

@v2_api_bp.route('/raw_new_test_patient', methods=['GET'])
def raw_new_test_patient():
    try:
        result = db.session.execute(text("SELECT * FROM new_test_patient;"))
        rows = result.fetchall()
        keys = result.keys()
        data = [dict(zip(keys, row)) for row in rows]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@v2_api_bp.route('/get_call_logs', methods=['GET', 'POST'])
def get_call_logs():
    data = request.get_json()
    
    if not data:
        return jsonify({"Error": "Invalid request, no JSON payload received"}), 400

    rxkid = data["rxkid"]

    patient = NewTestPatient.query.filter_by(rxkid=rxkid).first()

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    logs = CallLogs.query.filter_by(patient_id=patient.id).all()
    
    logs_data = [
        {
            "id": log.id,
            "call_date": log.call_date.isoformat() if log.call_date else None,
            "call_time": log.call_time.isoformat() if log.call_time else None,
            "admin_comment": log.admin_comment,
        }
        for log in logs
    ]
    return jsonify(logs_data), 200

@v2_api_bp.route('/update_call_logs', methods=['POST'])
def update_call_logs():
    try:
        data = request.get_json()
        rxkid = data["patientId"]
        patient = NewTestPatient.query.filter_by(rxkid=rxkid).first()

        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Get current max ID using SQLAlchemy core
        max_id = db.session.query(db.func.max(CallLogs.id)).scalar() or 0
        
        # Reset sequence using proper SQLAlchemy text() binding
        db.session.execute(
            text("SELECT setval('call_logs_id_seq', :new_val)"),
            {'new_val': max_id}
        )

        time_str = data["time"]
        # Determine if time_str is in 12-hour format with AM/PM or in 24-hour format
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            parsed_time = datetime.strptime(time_str, "%I:%M %p").time()
        else:
            parsed_time = datetime.strptime(time_str, "%H:%M").time()

        new_log = CallLogs(
            patient_id=patient.id,  # Explicit ID assignment
            call_date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            call_time=parsed_time,
            admin_comment=data["comment"]
        )

        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Call log added", "log_id": new_log.id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@v2_api_bp.route('/refresh_database', methods=['GET'])
def refreshEntireDataBase():
    print(f'This endpoint was triggered')
    from db.extensions import db
    # Drop all existing tables and create new ones
    db.drop_all()
    db.create_all()
    db.session.commit()

    import time 
    time.sleep(3)

    import requests
    base_url = "https://flask-nine-green.vercel.app"
    user_resp = requests.get(f"{base_url}/api/v2/populator/popluate_user_data")
    print(f'\n\n The user response api populator is as follows {user_resp}\n\n')
    patient_resp = requests.get(f"{base_url}/api/v2/populator/populate_given_patient_data")
    call_logs_resp = requests.get(f"{base_url}/api/v2/populator/populate_call_logs")
    key_code_logs = requests.get(f"{base_url}/api/v2/populator/update_key_codes")
    discharged_patients = requests.get(f"{base_url}/api/v2/populator/update_discharged_patients")
    assigned_patients = requests.get(f"{base_url}/api/v2/populator/update_assigned_patients_record")

    return jsonify({
        "user_data": user_resp.json(),
        "patient_data": patient_resp.json(),
        "call_logs": call_logs_resp.json(),
        "key_code_logs": key_code_logs.json(),
        "discharged_patients": discharged_patients.json(),
        "assigned_patients": assigned_patients.json()
    }), 200

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
        total_waiting = Patient.query.c(status="Waiting").count()
        total_procedures = Patient.query.filter_by(status="Procedure").count()
        total_discharged = Patient.query.filter_by(status="Discharged").count()

        return jsonify({
            "total_waiting": total_waiting,
            "total_procedures": total_procedures,
            "total_discharged": total_discharged
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@v2_api_bp.route('/get_stats', methods=['GET'])
def get_stats():
    try:
        total_dna = NewTestPatient.query.filter_by(key_code="0 - Cancellation or DNA").count()
        total_bkd_proce = NewTestPatient.query.filter_by(key_code="1 - Booked for procedure").count()
        total_bkd_pre_asses = NewTestPatient.query.filter_by(key_code="2 - Booked for pre-assessment").count()
        total_ong_proce = NewTestPatient.query.filter_by(key_code="3- Ongoing Procedure").count()
        total_discharged = NewTestPatient.query.filter_by(key_code="4 - Discharged").count()
        total_wl = NewTestPatient.query.filter_by(key_code="N/A").count()

        return jsonify({
            "total_dna": total_dna,
            "total_bkd_proce": total_bkd_proce,
            "total_bkd_pre_asses": total_bkd_pre_asses,
            "total_ong_proce": total_ong_proce,
            "total_discharged": total_discharged,
            "total_wl": total_wl
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@v2_api_bp.route('/custom_data_fetching', methods=['GET', 'POST'])
def custom_fetcher():
    # Expect the key_code parameter in the query string
    data = request.get_json()
    key_code = data["key_code"]

    if not key_code:
        return jsonify({"error": "Missing key_code parameter"}), 400

    try:
        # Filter NewTestPatient records based on the provided key_code
        patients = NewTestPatient.query.filter_by(key_code=key_code).all()
        data = [
            {
                "id": patient.id,
                "external_id": patient.external_id,
                "reporting_status": patient.reporting_status,
                "test_type_main": patient.test_type_main,
                "test_type": patient.test_type,
                "waitlist_name": patient.waitlist_name,
                "rxkid": patient.rxkid,
                "surname": patient.surname,
                "forename": patient.forename,
                "points": patient.points,
                "requires_pre_add": patient.requires_pre_add,
                "key_code": patient.key_code,
                "comment": patient.comment,
                "dated": patient.dated,
                "sub_type": patient.sub_type,
                "referral_priority": patient.referral_priority,
                "date_added_to_wl": patient.date_added_to_wl,
                "adj_wl_start": patient.adj_wl_start,
                "remvl_dttm": patient.remvl_dttm,
                "weeks_wait": patient.weeks_wait,
                "current_rtt_waits": patient.current_rtt_waits,
                "indication": patient.indication,
                "appointment_date": patient.appointment_date,
                "appt_by_date_ipm": patient.appt_by_date_ipm,
                "appt_by_date_calculated": patient.appt_by_date_calculated,
                "short_notice_flag": patient.short_notice_flag,
            }
            for patient in patients
        ]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@v2_api_bp.route('/assign_patient', methods=['POST'])
def assign_patient():
    data = request.get_json()

    try:
        # Extract data
        patient_rxkid = data["patient_id"]  # Assuming this is rxkid
        assigned_clinician = data["assigned_to"]
        cli_fname, cli_lname = assigned_clinician.split(" ")

        # Get Clinician ID
        clinician = User.query.filter_by(fname=cli_fname, lname=cli_lname).first()
        if not clinician:
            return jsonify({"error": "Clinician not found"}), 404

        # Get Patient ID using rxkid
        patient = NewTestPatient.query.filter_by(rxkid=patient_rxkid).first()
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Assign patient to clinician
        assignment = AssignPatient(patient_id=patient.id, clinician_id=clinician.id)
        db.session.add(assignment)

        # Update key_code to "1 - Booked for procedure"
        patient.key_code = "1 - Booked for procedure"
        db.session.commit()

        print(f'Clinician ID: `{clinician.id}` assigned to Patient ID: `{patient.id}`, Key Code Updated')

        return jsonify({
            "message": "Patient successfully assigned",
            "clinician_id": clinician.id,
            "patient_id": patient.id,
            "updated_key_code": patient.key_code
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f'Error: {str(e)}')
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@v2_api_bp.route('/ongoing_procedures', methods=['POST'])
def onGoing_procedures():
    data = request.get_json()

    user_role = data.get("user_role")
    clinician_fname = data.get("fname")
    clinician_lname = data.get("lname")

    try:
        if user_role == "Clinician":
            # Step 1: Fetch Clinician ID
            clinician = User.query.filter_by(fname=clinician_fname, lname=clinician_lname).first()
            if not clinician:
                return jsonify({"error": "Clinician not found"}), 404

            # Step 2: Get Assigned Patients for This Clinician
            assigned_patients = AssignPatient.query.filter_by(clinician_id=clinician.id).all()

        elif user_role == "Admin":
            # Admin case: Fetch all assigned patients (no clinician filtering)
            assigned_patients = AssignPatient.query.all()
        else:
            return jsonify({"error": "Invalid user role"}), 400  # Handle unexpected roles

        if not assigned_patients:
            return jsonify({"message": "No assigned patients found"}), 200

        # Step 3: Fetch Patient Details from NewTestPatient Table
        patient_ids = [assignment.patient_id for assignment in assigned_patients]
        patients = NewTestPatient.query.filter(NewTestPatient.id.in_(patient_ids)).all()

        # Step 4: Format the response data to match the frontend schema
        patient_data = [{
            "id": patient.id,
            "forename": patient.forename,
            "surname": patient.surname,
            "waitlist_name": patient.waitlist_name,
            "key_code": patient.key_code,
            "test_type": patient.test_type,
            "test_type_main": patient.test_type_main,
            "rxkid": patient.rxkid,
            "reporting_status": patient.reporting_status,
            "points": patient.points,
            "requires_pre_add": patient.requires_pre_add,
            "comment": patient.comment,
            "dated": patient.dated,
            "sub_type": patient.sub_type,
            "referral_priority": patient.referral_priority,
            "date_added_to_wl": patient.date_added_to_wl,
            "adj_wl_start": patient.adj_wl_start,
            "remvl_dttm": patient.remvl_dttm,
            "weeks_wait": patient.weeks_wait,
            "current_rtt_waits": patient.current_rtt_waits,
            "indication": patient.indication,
            "appointment_date": patient.appointment_date,
            "appt_by_date_ipm": patient.appt_by_date_ipm,
            "appt_by_date_calculated": patient.appt_by_date_calculated,
            "short_notice_flag": patient.short_notice_flag
        } for patient in patients]

        return jsonify({"patients": patient_data}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
@v2_api_bp.route("/discharge_patients", methods=['POST'])
def dischargePatients():
    data = request.get_json()
    rxkid = data["rxkid"]
    discharge_notes = data.get("discharge_notes")
    recovery_instructions = data.get("recovery_instructions")
    
    try:
        # Get the patient by exact rxkid match
        patient = NewTestPatient.query.filter_by(rxkid=rxkid).first()
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Delete the assignment row in assign_patient table using patient.id
        assignment = AssignPatient.query.filter_by(patient_id=patient.id).first()
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        clinician_id = assignment.clinician_id
        db.session.delete(assignment)
        
        # Update the Patient's Status
        patient.key_code = "4 - Discharged"

        # Insert a new record into DischargedPatients table
        discharged_patient = DischargedPatients(
            patient_id=patient.id,
            clinician_id=clinician_id,
            discharge_notes=discharge_notes,
            recovery_instructions=recovery_instructions
        )
        db.session.add(discharged_patient)
        db.session.commit()
        
        return jsonify({"message": "Patient discharged successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    

@v2_api_bp.route("/get_discharged_patients", methods=['GET'])
def fetchDischargedPatients():
    try:
        # Step 1: Get discharged patient records
        discharged_records = DischargedPatients.query.all()
        if not discharged_records:
            return jsonify({"message": "No discharged patients found"}), 200

        # Step 2: Extract patient IDs from discharged records
        patient_ids = [record.patient_id for record in discharged_records]

        # Step 3: Fetch matching patients from new_test_patient table
        patients = NewTestPatient.query.filter(NewTestPatient.id.in_(patient_ids)).all()

        # Step 4: Format the response data to match the frontend schema
        patient_data = [{
            "id": patient.id,
            "forename": patient.forename,
            "surname": patient.surname,
            "waitlist_name": patient.waitlist_name,
            "key_code": patient.key_code,
            "test_type": patient.test_type,
            "test_type_main": patient.test_type_main,
            "rxkid": patient.rxkid,
            "reporting_status": patient.reporting_status,
            "points": patient.points,
            "requires_pre_add": patient.requires_pre_add,
            "comment": patient.comment,
            "dated": patient.dated,
            "sub_type": patient.sub_type,
            "referral_priority": patient.referral_priority,
            "date_added_to_wl": patient.date_added_to_wl,
            "adj_wl_start": patient.adj_wl_start,
            "remvl_dttm": patient.remvl_dttm,
            "weeks_wait": patient.weeks_wait,
            "current_rtt_waits": patient.current_rtt_waits,
            "indication": patient.indication,
            "appointment_date": patient.appointment_date,
            "appt_by_date_ipm": patient.appt_by_date_ipm,
            "appt_by_date_calculated": patient.appt_by_date_calculated,
            "short_notice_flag": patient.short_notice_flag
        } for patient in patients]

        return jsonify({"patients": patient_data}), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@v2_api_bp.route("/get_discharged_patients_from_key_code", methods=['GET'])
def fetchDischargedPatientsV2():
    try:
        key_code = "4 - Discharged"
        discharged_patients = NewTestPatient.query.filter_by(key_code=key_code).all()
        
        if not discharged_patients:
            return jsonify({"message": "No discharged patients found"}), 200

        patient_ids = [patient.id for patient in discharged_patients]

        # Retrieve discharge records for these patients
        discharge_records = DischargedPatients.query.filter(DischargedPatients.patient_id.in_(patient_ids)).all()
        clinician_ids = {record.patient_id: record.clinician_id for record in discharge_records}
        discharge_notes_map = {record.patient_id: record.discharge_notes for record in discharge_records}
        recovery_instructions_map = {record.patient_id: record.recovery_instructions for record in discharge_records}

        # Retrieve clinician details
        clinician_details = {clinician.id: f"Dr. {clinician.fname} {clinician.lname}" for clinician in User.query.filter(User.id.in_(clinician_ids.values())).all()}

        # Prepare response data
        data = [
            {
                "id": patient.id,
                "external_id": patient.external_id,
                "reporting_status": patient.reporting_status,
                "test_type_main": patient.test_type_main,
                "test_type": patient.test_type,
                "waitlist_name": patient.waitlist_name,
                "rxkid": patient.rxkid,
                "surname": patient.surname,
                "forename": patient.forename,
                "points": patient.points,
                "requires_pre_add": patient.requires_pre_add,
                "key_code": patient.key_code,
                "comment": patient.comment,
                "dated": patient.dated,
                "sub_type": patient.sub_type,
                "referral_priority": patient.referral_priority,
                "date_added_to_wl": patient.date_added_to_wl,
                "adj_wl_start": patient.adj_wl_start,
                "remvl_dttm": patient.remvl_dttm,
                "weeks_wait": patient.weeks_wait,
                "current_rtt_waits": patient.current_rtt_waits,
                "indication": patient.indication,
                "appointment_date": patient.appointment_date,
                "appt_by_date_ipm": patient.appt_by_date_ipm,
                "appt_by_date_calculated": patient.appt_by_date_calculated,
                "short_notice_flag": patient.short_notice_flag,
                "assigned_too": clinician_details.get(clinician_ids.get(patient.id), "Not Assigned"),
                "discharge_notes": discharge_notes_map.get(patient.id, ""),
                "recovery_instructions": recovery_instructions_map.get(patient.id, "")
            }
            for patient in discharged_patients
        ]

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500



