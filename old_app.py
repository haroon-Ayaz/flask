# import json
# from flask import Flask, request, jsonify, session
# from functools import wraps
# from flask_cors import CORS
# import sys
# import os
#
# # Ensure project root is in sys.path
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
#
# from db.extensions import db, bcrypt
# from db.models import User, Patient
#
# app = Flask(__name__)
# CORS(app)
#
# # SQLite Database Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db.init_app(app)
# bcrypt.init_app(app)
#
# from api.routes import api_bp
# app.register_blueprint(api_bp, url_prefix='/api')
#
# with app.app_context():
#     db.create_all()
#
# # db = SQLAlchemy(app)
# # bcrypt = Bcrypt(app)
# #
# # # User Model
# # class User(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     email = db.Column(db.String(120), unique=True, nullable=False)
# #     password = db.Column(db.String(120), nullable=False)
# #     role = db.Column(db.String(10), nullable=False)
# #
# # # Patient Model
# # class Patient(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     title = db.Column(db.String(10), nullable=False)
# #     fname = db.Column(db.String(120), nullable=False)
# #     lname = db.Column(db.String(120), nullable=False)
# #     phone_number = db.Column(db.String(20), unique=True, nullable=False)
# #     home_number = db.Column(db.String(20), nullable=False)
# #     problem = db.Column(db.Text, nullable=False)
# #     address = db.Column(db.String(255), nullable=False)
# #     postcode = db.Column(db.String(20), nullable=False)
# #     assigned_to = db.Column(db.String(120), nullable=True)
# #     status = db.Column(db.String(20), default="Waiting")
# #
# # # Create Database Tables
# # with app.app_context():
# #     db.create_all()
# #
# # # Create Database Tables
# # with app.app_context():
# #     db.create_all()
#
# # Middleware to restrict access to authenticated users
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return jsonify({"message": "Unauthorized. Please log in."}), 401
#         return f(*args, **kwargs)
#     return decorated_function
#
# # @app.route('/getdata', methods=['GET'])
# # def get_data():
# #     try:
# #         patients = Patient.query.all()
# #         patient_list = [
# #             {
# #                 "id": patient.id,
# #                 "title": patient.title,
# #                 "fname": patient.fname,
# #                 "lname": patient.lname,
# #                 "address": patient.address,
# #                 "postcode": patient.postcode,
# #                 "phone_number": patient.phone_number,
# #                 "home_number": patient.home_number,
# #                 "problem": patient.problem
# #             }
# #             for patient in patients
# #         ]
# #         return jsonify(patient_list), 200
# #     except Exception as e:
# #         return jsonify({"message": f"Error: {str(e)}"}), 500
#
# @app.route('/assign_patient', methods=['POST'])
# def assign_patient():
#     data = request.get_json()
#     patient_id = data.get("patient_id")
#     clinician = data.get("clinician")
#
#     patient = Patient.query.get(patient_id)
#     if not patient:
#         return jsonify({"message": "Patient not found"}), 404
#
#     patient.assigned_to = clinician
#     patient.status = "Under Procedure"
#     db.session.commit()
#
#     return jsonify({"message": "Patient assigned successfully"}), 200
#
# # @app.route('/populatedata', methods=['GET'])
# # def populatedata():
# #     file_path = r"D:\Projects\NHS\flask-mvp\utils\patients.json"
# #
# #     if not os.path.exists(file_path):
# #         return jsonify({"message": "File not found"}), 404
# #
# #     try:
# #         with open(file_path, "r") as file:
# #             patients = json.load(file)
# #
# #         for patient in patients:
# #             new_patient = Patient(
# #                 title=patient["title"],
# #                 fname=patient["fname"],
# #                 lname=patient["lname"],
# #                 address=patient["address"],
# #                 postcode=patient["postcode"],
# #                 phone_number=patient["phone_number"],
# #                 home_number=patient["home_number"],
# #                 problem=patient["problem"]
# #             )
# #             db.session.add(new_patient)
# #
# #         db.session.commit()
# #         return jsonify({"message": "Patients data populated successfully"}), 201
# #
# #     except Exception as e:
# #         return jsonify({"message": f"Error: {str(e)}"}), 500
#
# @app.route('/addpatient', methods=['POST'])
# def add_patient():
#     data = request.get_json()
#     print(f'data: {data}')
#
#     title = data.get('title')
#     fname = data.get('fname')
#     lname = data.get('sname')
#     address = data.get('address')
#     postal_code = data.get('postcode')
#     mobile_number = data.get('mobilephone')
#     home_phone_number = data.get('homephone')
#     problem = data.get('problem')
#
#     print(f'title: {title}')
#     print(f'fname: {fname}')
#     print(f'lname: {lname}')
#     print(f'address: {address}')
#     print(f'postcode: {postal_code}')
#     print(f'mobile_number: {mobile_number}')
#     print(f'home_phone_number: {home_phone_number}')
#     print(f'problem: {problem}')
#
#     new_patient = Patient(
#         title=title,
#         fname=fname,
#         lname=lname,
#         address=address,
#         postcode=postal_code,
#         phone_number=mobile_number,
#         home_number=home_phone_number,
#         problem=problem
#     )
#
#     db.session.add(new_patient)
#     db.session.commit()
#
#     return jsonify({"message": "Patient added successfully!"}), 201
#
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get("email")
#     password = data.get("password")
#     if not email or not password:
#         return jsonify({"message": "Email and password are required"}), 400
#     user = User.query.filter_by(email=email).first()
#     if not user:
#         return jsonify({"message": "Invalid email or password"}), 401
#     print("Stored password hash:", user.password)  # Debugging
#     if not bcrypt.check_password_hash(user.password, password):
#         return jsonify({"message": "Invalid email or password"}), 401
#     session['user_id'] = user.id  # Store user session
#
#     return jsonify({
#         "message": "Login successful",
#         "email": user.email,
#         "role": user.role,
#     }), 200
#
# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     print(f'signup: {data}')
#     email = data.get("email")
#     password = data.get("password")
#     role = data.get("role")
#     if not email or not password or not role:
#         return jsonify({"message": "Incomplete Information"}), 400
#     existing_user = User.query.filter_by(email=email).first()
#     if existing_user:
#         return jsonify({"message": "This email is already registered"}), 400
#     hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#     new_user = User(email=email, password=hashed_password, role=role)
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({"message": "User created successfully"}), 201
#
# @app.route('/logout', methods=['POST'])
# @login_required
# def logout():
#     session.pop('user_id', None)
#     return jsonify({"message": "Logged out successfully"}), 200
#
# @app.route('/protected', methods=['GET'])
# @login_required
# def protected():
#     return jsonify({"message": "You have access to this protected route!"})
#
# @app.route('/')
# def home():
#     return jsonify({"message": "home"})
#
# if __name__ == '__main__':
#     app.run(debug=True)
