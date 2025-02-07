from flask import abort
from flask import Flask, jsonify, request
from flask_cors import CORS
import os, ssl
from dotenv import load_dotenv
from db.extensions import db
from db.models import Patient, User

load_dotenv()


ALLOWED_USER_AGENTS = ["Chrome/", "Firefox/", "Safari/", "Edg/", "Opera/"]

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

# Create tables (run this once)
with app.app_context():
    db.create_all()
    db.session.commit()

# Register blueprints
from api.routes import api_bp
from api.auth.authentication import auth_api_bp

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_api_bp, url_prefix='/api/custom-auth')

@app.route('/')
def home():
    return jsonify({"message": "home"})

@app.route('/test_api', methods=['GET', 'POST'])
def test_api():
    import random, string, time, uuid
    # Handle GET request
    if request.method == 'GET':
        return jsonify({
            'message': 'API is functional!',
            'random_number': random.randint(1, 1000),
            'timestamp': time.time(),
            'request_type': 'GET'
        }), 200
    
    # Handle POST request
    if request.method == 'POST':
        # Generate random response elements
        random_id = str(uuid.uuid4())
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Process incoming data
        post_data = {
            'received_data': request.json if request.is_json else request.form,
            'processing_id': random_id,
            'status': 'processed',
            'random_value': random_string,
            'server_timestamp': int(time.time())
        }

        return jsonify(post_data), 201

if __name__ == '__main__':
    app.run(debug=True)