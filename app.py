import shutil

from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from db.extensions import db, bcrypt

app = Flask(__name__)
CORS(app)

# Paths
TMP_DIR = os.path.join(os.getcwd(), "tmp")  # Use "tmp" inside project directory
ORIGINAL_DB_PATH = "instance/users.db"
TEMP_DB_PATH = os.path.join(TMP_DIR, "users.db")

# Ensure tmp directory exists
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)  # Create the directory if it doesn't exist

# Copy database if it doesn't exist in /tmp/
if not os.path.exists(TEMP_DB_PATH):
    shutil.copyfile(ORIGINAL_DB_PATH, TEMP_DB_PATH)

# SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{TEMP_DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)
bcrypt.init_app(app)

from api.routes import api_bp
from api.auth.authentication import auth_api_bp
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_api_bp, url_prefix='/api/auth')

with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/')
def home():
    return jsonify({"message": "home"})

@app.route('/test_write', methods=['POST'])
def test_write():
    try:
        with app.app_context():
            db.session.execute("INSERT INTO user (fname, lname, email, password, role) VALUES ('John', 'Doe', 'john@example.com', 'test', 'Admin')")
            db.session.commit()
        return {"message": "Write operation successful"}, 200
    except Exception as e:

if __name__ == '__main__':
    app.run(debug=True)