from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable cross-origin access
app.secret_key = 'secretkey123'       # Required for session tracking

# --- Simulated user database ---
# username: { password, role, display name }
users = {
    "patient1": {"password": "pass1", "role": "patient", "name": "Alice Smith"},
    "patient2": {"password": "pass2", "role": "patient", "name": "Bob Jones"},
    "doctor1": {"password": "docpass", "role": "doctor", "name": "Dr. Grey"},
    "frontdesk1": {"password": "deskpass", "role": "frontdesk", "name": "Receptionist One"}
}

# --- Simulated patient medical data ---
# Stored in-memory for this simulation
patient_data = {
    "patient1": {"prescriptions": [], "appointments": []},
    "patient2": {"prescriptions": [], "appointments": []}
}

# --- Shared medication inventory ---
medication_store = {
    "Tylenol": 50,
    "Ibuprofen": 20
}

# --- Doctor class handles clinical tasks ---
class Doctor:
    def __init__(self, name):
        self.name = name

    def view_patient_records(self):
        # Return a dictionary of all patients and their records
        return {
            pid: {
                "name": users[pid]["name"],
                "prescriptions": patient_data[pid]["prescriptions"],
                "appointments": patient_data[pid]["appointments"]
            } for pid in patient_data
        }

    def prescribe_medication(self, patient_id, medication):
        patient_data[patient_id]["prescriptions"].append(medication)

    def schedule_appointment(self, patient_id, date):
        patient_data[patient_id]["appointments"].append(date)

    def update_medication_store(self, name, qty):
        medication_store[name] = qty

# --- Patient class for viewing their own records ---
class Patient:
    def __init__(self, username):
        self.username = username
        self.data = patient_data.get(username, {"prescriptions": [], "appointments": []})

    def get_info(self):
        return self.data

    def add_prescription(self, prescription):
        self.data["prescriptions"].append(prescription)

    def add_appointment(self, date):
        self.data["appointments"].append(date)

# --- FrontDesk class for scheduling ---
class FrontDesk:
    def __init__(self, name="Receptionist"):
        self.name = name

    def get_all_appointments(self):
        return {pid: pdata.get("appointments", []) for pid, pdata in patient_data.items()}

    def set_appointment(self, patient_id, date):
        patient_data[patient_id]["appointments"].append(date)

# --- Routes ---

# Landing page redirects to login
@app.route('/')
def home():
    return render_template('login.html')

# Login validation and session setup
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    user = users.get(username)
    if user and user['password'] == password:
        session['username'] = username
        session['role'] = user['role']
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='Invalid credentials')

# Main dashboard route with role-based content
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['username']
    user = users[user_id]

    # Doctor dashboard
    if user['role'] == 'doctor':
        doctor = Doctor(user_id)

        if request.method == 'POST':
            patient_id = request.form.get('patient_id')
            if 'prescription' in request.form:
                doctor.prescribe_medication(patient_id, request.form['prescription'])
            if 'appointment' in request.form:
                doctor.schedule_appointment(patient_id, request.form['appointment'])

        records = doctor.view_patient_records()
        return render_template('dashboard_doctor.html', user=user, records=records)

    # FrontDesk dashboard
    if user['role'] == 'frontdesk':
        frontdesk = FrontDesk()
        if request.method == 'POST':
            patient_id = request.form['patient_id']
            appt_date = request.form['appointment']
            frontdesk.set_appointment(patient_id, appt_date)

        records = {
            pid: {"name": users[pid]["name"], "appointments": patient_data[pid]["appointments"]}
            for pid in patient_data
        }
        return render_template('dashboard_frontdesk.html', user=user, records=records, patient_ids=patient_data.keys())

    # Patient dashboard
    patient = Patient(user_id)
    return render_template('dashboard_patient.html', user=user, user_id=user_id, data=patient.get_info())

# View patient report page
@app.route('/patient/report')
def patient_report():
    if 'username' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))

    patient = Patient(session['username'])
    data = patient.get_info()
    return render_template('patient_report.html', patient=users[session['username']], data=data)

# Doctor medication inventory page
@app.route('/doctor/inventory', methods=['GET', 'POST'])
def inventory():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    doctor = Doctor(session['username'])

    if request.method == 'POST':
        med_name = request.form['med_name']
        quantity = int(request.form['quantity'])
        doctor.update_medication_store(med_name, quantity)

    return render_template('medication_inventory.html', meds=medication_store)

# Logout and clear session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
