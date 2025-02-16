import pandas as pd
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from db.models import TestPatient
from db.extensions import db

COLUMN_MAPPING = {
    "Reporting Status": "reporting_status",
    "Test Type main": "test_type_main",
    "Test Type": "test_type",
    "Waitlist Name": "waitlist_name",
    "Unitno": "unit_no",
    "SURNAME": "surname",
    "FORENAME": "forename",
    "Points": "points",
    "Requires Pre-Add": "requires_pre_add",
    "Key Code": "key_code",
    "Comment": "comment",
    "Dated": "dated",
    "Sub Type": "sub_type",
    "Referral Priority": "referral_priority",
    "Date Added to WL": "date_added_to_wl",
    "Adj WL Start": "adj_wl_start",
    "Waitlist Name 2": "waitlist_name_2",  # If you have a second "Waitlist Name" column
    "REMVL DTTM": "remvl_dttm",
    "Weeks Wait": "weeks_wait",
    "Current RTT Waits": "current_rtt_waits",
    "Indication": "indication",
    "ID": "rxkid",  # If you want to store the Excel 'ID' into 'rxkid'
    "Appointment Date": "appointment_date",
    "Appt By Date (IPM)": "appt_by_date_ipm",
    "Appt By Date (Calculated)": "appt_by_date_calculated",
    "SHORT NOTICE FLAG": "short_notice_flag",
}

def populate_test_patients_from_excel(filepath):
    # Read the Excel file
    df = pd.read_excel(filepath)
    
    # Optional: rename columns if you have exact duplicates, e.g.:
    # df.rename(columns={"Waitlist Name": "Waitlist Name 2"}, inplace=True)
    # Adjust the above if you have multiple columns with the same name.
    
    for _, row in df.iterrows():
        # Build a dictionary of model-field -> value
        record_data = {}
        
        for excel_col, model_field in COLUMN_MAPPING.items():
            # Safely retrieve the cell value from the row
            value = row.get(excel_col, None)
            
            # If the cell is NaN or empty, make it None
            if pd.isnull(value):
                value = None
            
            # Convert date-like fields if needed
            if model_field in [
                "dated", "date_added_to_wl", "adj_wl_start",
                "remvl_dttm", "appointment_date", "appt_by_date_ipm",
                "appt_by_date_calculated"
            ]:
                # Attempt to parse as a date if not None
                if value is not None:
                    try:
                        value = pd.to_datetime(value)
                    except Exception:
                        value = None  # or handle parsing error
            
            # Convert numeric fields if needed (e.g., 'points')
            if model_field == "points" and value is not None:
                try:
                    value = int(value)
                except ValueError:
                    value = None
            
            record_data[model_field] = value
        
        # If your model requires certain fields to be non-null
        # but your Excel might have them empty, handle that logic here:
        # e.g., if 'rxkid' is required, generate something or skip:
        if not record_data.get("rxkid"):
            # generate a unique fallback or skip this row
            # record_data["rxkid"] = str(uuid.uuid4())
            pass
        
        # Create the model instance
        test_patient = TestPatient(**record_data)
        
        # Add to the session
        db.session.add(test_patient)
    
    # Commit all at once
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        print("Error inserting rows:", e)
