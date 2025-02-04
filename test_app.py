import ssl

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, json
from dotenv import load_dotenv
# Initialize extensions
from db.extensions import db
from db.models import Patient
# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set SQLAlchemy engine options
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Automatically check connection health
    'pool_recycle': 3600,   # Recycle connections after 1 hour
    'pool_size': 10,        # Maintain up to 10 connections
    'max_overflow': 20,     # Allow up to 20 additional connections
    'connect_args': {
        'sslmode': 'require',
        'sslrootcert': ssl.get_default_verify_paths().openssl_cafile  # Use system CA
    }
}

# Initialize database
db.init_app(app=app)

# Create tables (run this once)
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()

# Test route
@app.route('/')
def hello():
    return "Database connected successfully!" if db.session.execute('SELECT 1').first() else "Connection failed"

@app.route('/populate_patient_data', methods=['GET'])
def populatedata():
    file_path = r"D:\Projects\NHS\flask-mvp\utils\patients.json"

    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    try:
        with open(file_path, "r") as file:
            patients = json.load(file)

        db.session.execute(db.delete(Patient))

        db.session.bulk_insert_mappings(Patient, patients)
        db.session.commit()

        # for patient in patients:
        #     try:
        #         new_patient = Patient(
        #             rxkid=patient["rxkid"],
        #             title=patient["title"],
        #             fname=patient["fname"],
        #             lname=patient["lname"],
        #             address=patient["address"],
        #             postcode=patient["postcode"],
        #             phone_number=patient["phone_number"],
        #             home_number=patient["home_number"],
        #             problem=patient["problem"],
        #             assigned_to=patient["assignto"],
        #             status=patient["status"],
        #         )
        #         db.session.add(new_patient)
        #         db.session.commit()  # Commit after each insert
        #         db.session.expunge_all()  # Clear session cache
        #     except Exception as e:
        #         db.session.rollback()  # Rollback failed transaction
        #         print(f"Failed to insert patient {patient['rxkid']}: {str(e)}")
        #         continue

        return jsonify({"message": "Patients data populated successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/getdata', methods=['GET'])
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



if __name__ == '__main__':
    app.run(debug=True)