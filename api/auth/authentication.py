from flask import request, jsonify, Blueprint, session
from db.models import User
from db.extensions import db, bcrypt
from functools import wraps

auth_api_bp = Blueprint('api/auth', __name__, url_prefix='/api/auth')

# Middleware to restrict access to authenticated users
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "Unauthorized. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401
    print("Stored password hash:", user.password)  # Debugging
    if password != user.password:
        return jsonify({"message": "Invalid email or password"}), 401
    session['user_id'] = user.id  # Store user session

    return jsonify({
        "message": "Login successful",
        "email": user.email,
        "role": user.role,
        "fname": user.fname,
        "lname": user.lname
    }), 200

@auth_api_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    print(f'signup: {data}')
    fname = data.get("fname")
    lname = data.get("lname")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    print(f'Data Recieved: {data}')
    print(f'fname:{fname}, lname:{lname}, email:{email}, password:{password}s')
    if not email or not password or not role or not fname or not lname:
        return jsonify({"message": "Incomplete Information"}), 400
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "This email is already registered"}), 400
    new_user = User(
        fname=fname, lname=lname, email=email,
        password=password, role=role
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@auth_api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200
