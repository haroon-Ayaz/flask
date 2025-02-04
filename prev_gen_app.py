from flask import Flask, jsonify
from flask_cors import CORS
import os
import shutil

app = Flask(__name__)
CORS(app)

# Vercel-specific paths
ORIGINAL_DB_PATH = os.path.join(os.getcwd(), 'instance', 'users.db')
TEMP_DB_PATH = '/tmp/users.db'  # Use Vercel's writable /tmp directly

# Copy database to writable location if it doesn't exist
if not os.path.exists(TEMP_DB_PATH) and os.path.exists(ORIGINAL_DB_PATH):
    shutil.copyfile(ORIGINAL_DB_PATH, TEMP_DB_PATH)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{TEMP_DB_PATH}?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize extensions
from db.extensions import db, bcrypt
db.init_app(app)
bcrypt.init_app(app)

# Register blueprints
from api.routes import api_bp
from api.auth.authentication import auth_api_bp
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_api_bp, url_prefix='/api/auth')

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return jsonify({"message": "home"})

if __name__ == '__main__':
    app.run(debug=True)