from db.extensions import db

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)

# Patient Model
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rxkid = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(10), nullable=False)
    fname = db.Column(db.String(120), nullable=False)
    lname = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.Text, unique=True, nullable=False)
    home_number = db.Column(db.Text, nullable=False)
    problem = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    postcode = db.Column(db.String(20), nullable=False)
    assigned_to = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), default="Waiting")