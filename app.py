from flask import Flask, jsonify
from flask_cors import CORS
import os, ssl
from dotenv import load_dotenv
from db.extensions import db
from db.models import Patient, User

load_dotenv()

app = Flask(__name__)
CORS(app)

# Retrieve the DATABASE_URL environment variable
database_url = os.getenv('DATABASE_URL')
if database_url is None:
    raise ValueError("DATABASE_URL environment variable is not set.")

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

# Create tables (run this once)
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()

# Register blueprints
from api.routes import api_bp
from api.auth.authentication import auth_api_bp

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_api_bp, url_prefix='/api/auth')

@app.route('/')
def home():
    return jsonify({"message": "home"})

if __name__ == '__main__':
    app.run(debug=True)