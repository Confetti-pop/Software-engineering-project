from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable cross-origin access
app.secret_key = 'secretkey123'       # Required for session tracking

# --- Simulated user database ---
# username: { password, role, display name }
users = {
    "patient1": {
        "password": "pass1",
        "role": "patient",
        "name": "Alice Smith",
        "appointments": []
    },
    "patient2": {
        "password": "pass2",
        "role": "patient",
        "name": "Bob Jones",
        "appointments": []
    },
    "doctor1": {
        "password": "docpass",
        "role": "doctor",
        "name": "Dr. Grey"
    },
    "frontdesk1": {
        "password": "frontpass",
        "role": "frontdesk",
        "name": "Reception Staff"
    }
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
    print("✅ Entered /dashboard route")
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Safely retrieve user ID from session
        user_id = session['username']
        user = users[user_id]

        # DEBUG print
        print(f"🔍 Dashboard access by {user_id} with role {user['role']}")

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

        elif user['role'] == 'patient':
            patient = Patient(user_id)
            info = patient.get_info()
            return render_template('dashboard_patient.html', user=user, user_id=user_id, data=info)

        elif user['role'] == 'frontdesk':
            fd = FrontDesk(user_id)

            if request.method == 'POST':
                patient_id = request.form.get('patient_id')
                appointment = request.form.get('appointment')
                fd.schedule_patient_appointment(patient_id, appointment)

            records = {
                pid: {"name": users[pid]["name"], "appointments": patient_data[pid]["appointments"]}
                for pid in patient_data
            }
            return render_template(
                'dashboard_frontdesk.html',
                user=user,
                records=records,
                patient_ids=patient_data.keys()
            )

        else:
            return "Invalid role", 403

    except Exception as e:
        print(f"❌ Error in /dashboard: {e}")
        return "Dashboard failed to load", 500

# FrontDesk dashboard
@app.route('/dashboard/frontdesk', methods=['GET', 'POST'])
def frontdesk_dashboard():
    # Retrieve the logged-in user's ID from the session
    user_id = session.get('username')  # the username is stored in session
    user = users.get(user_id)          # get full user object/dictionary from users

    # Make sure the user exists and is a front desk
    if not user or user['role'] != 'frontdesk':
        return redirect(url_for('login'))  # redirect to login if unauthorized

    frontdesk = FrontDesk()

    # If an appointment is being set via form submission
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        appt_date = request.form.get('appointment')
        frontdesk.set_appointment(patient_id, appt_date)

    # Prepare the records to show patient info
    records = {
        pid: {
            "name": users[pid]["name"],
            "appointments": patient_data[pid]["appointments"]
        }
        for pid in patient_data
    }

    return render_template(
        'dashboard_frontdesk.html',
        user=user,
        records=records,
        patient_ids=patient_data.keys()
    )

# Patient dashboard
@app.route('/dashboard/patient')
def patient_dashboard():
    # Get the currently logged-in user's ID
    user_id = session.get('username')  # from session during login
    user = users.get(user_id)          # fetch user data from users dictionary

    # If user is not found or is not a patient, redirect to login
    if not user or user['role'] != 'patient':
        return redirect(url_for('login'))

    # Create a dummy Patient object (only if needed for get_info())
    patient = Patient(user_id)

    return render_template(
        'dashboard_patient.html',
        user=user,
        user_id=user_id,
        data=patient.get_info()
    )

# View patient report page
@app.route("/patient_report")
def patient_report():
    return render_template("patient_report.html")

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

# View appointment history page
@app.route("/appointment_history")
def appointment_history():
    return render_template("appointment_history.html")

# Analytics Dashboard Route
@app.route('/analytics')
def analytics_dashboard():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get the current user info
    user = users[session['username']]

    # Restrict access: only doctor or front desk can view analytics
    if user['role'] not in ['doctor', 'frontdesk']:
        return "Access denied", 403

    # Calculate total number of patients in the system
    total_patients = sum(1 for u in users.values() if u['role'] == 'patient')

    # Calculate total number of appointments (all patients combined)
    total_appointments = sum(len(u.get('appointments', [])) for u in users.values() if u['role'] == 'patient')

    # Calculate the most prescribed medications
    medication_counts = {}
    for patient_id, info in patient_data.items():
        for med in info.get('prescriptions', []):
            medication_counts[med] = medication_counts.get(med, 0) + 1

    # Render the analytics dashboard template
    return render_template(
        'analytics_dashboard.html',
        total_patients=total_patients,
        total_appointments=total_appointments,
        medication_counts=medication_counts
    )
# Scheduling appointment
@app.route("/schedule_appointment")
def schedule_appointment():
    return render_template("schedule_appointment.html")

# Confirming appointment
@app.route('/confirm_appointment')
def confirm_appointment():
    doctor_name = request.args.get('doctor', 'Unknown Doctor')
    return render_template('confirm_appointment.html', doctor_name=doctor_name)

@app.route('/appointment_success', methods=['POST'])
def appointment_success():
    doctor = request.form['doctor']
    date = request.form['date']
    time = request.form['time']
    return f"Appointment confirmed with {doctor} on {date} at {time}!"

@app.route("/checkin_success", methods=["POST"])
def checkin_success():
    # You can optionally grab submitted form data if you want:
    patient_name = request.form.get("patient_name")
    appointment_id = request.form.get("appointment_id")

# Flash the success message
    flash(f"Patient {patient_name} (Appointment ID: {appointment_id}) checked in successfully!")

    return render_template("checkin_success.html")

# Logout and clear session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
