from flask import abort, Flask, jsonify, request
from flask_cors import CORS
import os, ssl
from dotenv import load_dotenv
from db.extensions import db
from db.models import Patient, User
import requests  # Only needed if you choose to use requests instead of test_client

load_dotenv()

ALLOWED_USER_AGENTS = ["Chrome/", "Firefox/", "Safari/", "Edg/", "Opera/"]

def create_app():
    app = Flask(__name__)
    # Configure CORS with specific options
    CORS(app, 
        resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "expose_headers": ["Access-Control-Allow-Origin"],
                "max_age": 3600  # Cache preflight for 1 hour
            }
        }
    )

    database_url = "postgresql://neondb_owner:npg_mX6s3WplMxPy@ep-red-breeze-a236w9iq-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"
    # Replace 'postgres://' with 'postgresql://' if present
    database_url = database_url.replace('postgres://', 'postgresql://')

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'

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

    # Register blueprints
    from api.routes import api_bp
    from api.auth.authentication import auth_api_bp
    from api.v2.routes import v2_api_bp
    from api.v2.populator import populator_api

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(v2_api_bp, url_prefix='/api/v2')
    app.register_blueprint(auth_api_bp, url_prefix='/api/custom-auth')
    app.register_blueprint(populator_api, url_prefix='/api/v2/populator')

    @app.route('/')
    def home():
        return jsonify({"message": "home"})

    # ONLY RUN IN MAIN PROCESS - NO RELOADER
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        with app.app_context():
            if os.environ.get('REFRESH_DB') == '1':  # Add control flag
                refresh_database(app)
    return app

def refresh_database(app):
    print('Refreshing the database...')
    from db.extensions import db
    db.drop_all()
    db.create_all()
    db.session.commit()

    import time 
    time.sleep(3)

    endpoints = [
        "/api/v2/populator/popluate_user_data",
        "/api/v2/populator/populate_given_patient_data",
        "/api/v2/populator/populate_call_logs",
        "/api/v2/populator/update_key_codes",
        "/api/v2/populator/update_discharged_patients", 
        "/api/v2/populator/update_assigned_patients_record",
    ]

    responses = {}
    with app.test_client() as client:
        for endpoint in endpoints:
            resp = client.get(endpoint)
            responses[endpoint] = resp.get_json() if resp.is_json else resp.data.decode()
            print(f"Called {endpoint} with response: {responses[endpoint]}")
    
    print('Database refresh and data population complete.')
    return responses

if __name__ == '__main__':
    os.environ['REFRESH_DB'] = '1'
    app = create_app()
    app.run(debug=True)
