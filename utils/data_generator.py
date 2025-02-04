import json
import random
from faker import Faker

fake = Faker()

def generate_patient_data(num_patients=100):
    titles = ["Mr.", "Mrs."]
    status_options = ["Waiting", "Procedure", "Discharged"]
    clinicians = ["Mathew John", "Sarah Johnson", "Michael Chen", "Emma Wilson", "James Rodriguez", "Olivia Smith"]

    patients = []

    for _ in range(num_patients):
        status = random.choice(status_options)
        patient = {
            "rxkid": "RXK" + str(fake.random_number(fix_len=True, digits=6)),
            "title": random.choice(titles),
            "fname": fake.first_name(),
            "lname": fake.last_name(),
            "address": fake.address(),
            "postcode": fake.postcode(),
            "phone_number": fake.phone_number(),
            "home_number": fake.phone_number(),
            "problem": fake.sentence(nb_words=6),
            "assigned_to": random.choice(clinicians) if status == "Procedure" else None,
            "status": status,
        }
        patients.append(patient)

    with open("patients.json", "w") as file:
        json.dump(patients, file, indent=4)

    return "patients.json generated successfully."

# Generate and save patient data
generate_patient_data()
