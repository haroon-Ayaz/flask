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

class TestPatient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rxkid = db.Column(db.String(120), unique=True, nullable=False)
    reporting_status = db.Column(db.String(50), nullable=False)
    test_type_main = db.Column(db.String(50), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    waitlist_name = db.Column(db.String(120), nullable=False)
    unit_no = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    forename = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    requires_pre_add = db.Column(db.String(10), nullable=True)
    key_code = db.Column(db.String(50), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    dated = db.Column(db.DateTime, nullable=True)
    sub_type = db.Column(db.String(50), nullable=True)
    referral_priority = db.Column(db.String(50), nullable=True)
    date_added_to_wl = db.Column(db.DateTime, nullable=True)
    adj_wl_start = db.Column(db.DateTime, nullable=True)
    waitlist_name_2 = db.Column(db.String(120), nullable=True)
    remvl_dttm = db.Column(db.DateTime, nullable=True)
    weeks_wait = db.Column(db.String(50), nullable=True)
    current_rtt_waits = db.Column(db.String(250), nullable=True)
    indication = db.Column(db.Text, nullable=True)
    appointment_date = db.Column(db.DateTime, nullable=True)
    appt_by_date_ipm = db.Column(db.DateTime, nullable=True)
    appt_by_date_calculated = db.Column(db.DateTime, nullable=True)
    short_notice_flag = db.Column(db.String(5), nullable=True)

class NewTestPatient(db.Model):
    __tablename__ = 'new_test_patient'

    # Default auto-increment primary key (used as a serial number in the frontend)
    id = db.Column(db.Integer, primary_key=True)

    # External ID from the JSON "ID" field; optional if you don't need to enforce uniqueness
    external_id = db.Column(db.Integer, nullable=True)

    # Fields from the JSON, mapped to the new schema:
    reporting_status = db.Column(db.String(50), nullable=False)
    test_type_main = db.Column(db.String(50), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    waitlist_name = db.Column(db.String(120), nullable=False)
    
    # Rename "Unitno" from the JSON to "rxkid" here
    rxkid = db.Column(db.String(50), nullable=False)

    surname = db.Column(db.String(120), nullable=False)
    forename = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    requires_pre_add = db.Column(db.String(10), nullable=True)
    key_code = db.Column(db.String(50), nullable=True)
    comment = db.Column(db.Text, nullable=True)

    # "Dated" in JSON is "Y" or "N", so we store it as a short string
    dated = db.Column(db.String(10), nullable=True)
    
    sub_type = db.Column(db.String(50), nullable=True)
    referral_priority = db.Column(db.String(50), nullable=True)

    # Date/time fields from the JSON are stored as strings since they can be ISO dates or "N/A"
    date_added_to_wl = db.Column(db.String(50), nullable=True)
    adj_wl_start = db.Column(db.String(50), nullable=True)
    remvl_dttm = db.Column(db.String(50), nullable=True)
    
    # Weeks Wait can be an integer, but to accommodate potential "N/A" we store it as string
    weeks_wait = db.Column(db.String(50), nullable=True)
    
    current_rtt_waits = db.Column(db.String(250), nullable=True)
    indication = db.Column(db.Text, nullable=True)
    appointment_date = db.Column(db.String(50), nullable=True)
    appt_by_date_ipm = db.Column(db.String(50), nullable=True)
    appt_by_date_calculated = db.Column(db.String(50), nullable=True)
    short_notice_flag = db.Column(db.String(5), nullable=True)
