from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from flask_cors import CORS
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable cross-origin access
app.secret_key = 'secretkey123'       # Required for session tracking
appointments = []                     # In-Memory Appointment Storage 

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
    "drsmith": {
        "password": "cardio123",
        "role": "doctor",
        "name": "Dr. Smith"
    },
    "drwilliams": {
        "password": "radio123",
        "role": "doctor",
        "name": "Dr. Williams"
    },
    "drwilson": {
        "password": "onco123",
        "role": "doctor",
        "name": "Dr. Wilson"
    },
    "drjohnson": {
        "password": "rheuma123",
        "role": "doctor",
        "name": "Dr. Johnson"
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
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    
    role = session.get("role")

    if role == "patient":
        return redirect("/dashboard_patient")
    elif role == "doctor":
        return redirect("/dashboard_doctor")
    elif role == "frontdesk":
        return redirect("/dashboard_frontdesk")
    else:
        return redirect("/login")

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
    if "username" in session and session.get("role") == "patient":
        patient = {
            "name": session["username"]
        }
        return render_template("patient_report.html", patient=patient)
    else:
        flash("Access denied. Please log in as a patient.")
        return redirect("/login")

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
    username = session.get("username")
    user_appointments = [appt for appt in appointments if appt["patient"] == username]
    return render_template("appointment_history.html", appointments=user_appointments)

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
    doctors = [
        {
            "name": "Dr. Smith",
            "specialty": "Cardiologist",
            "contact": "(832)100-9000",
            "building": "321",
            "address": "1 Main St, Houston, TX 77002"
        },
        {
            "name": "Dr. Williams",
            "specialty": "Radiologist",
            "contact": "(832)200-8000",
            "building": "654",
            "address": "1 Main St, Houston, TX 77021"
        },
        {
            "name": "Dr. Wilson",
            "specialty": "Oncologist",
            "contact": "(832)300-7000",
            "building": "987",
            "address": "1 Main St, Houston, TX 77002"
        },
        {
            "name": "Dr. Johnson",
            "specialty": "Rheumatologist",
            "contact": "(832)400-6000",
            "building": "741",
            "address": "1 Main St, Houston, TX 77002"
        }
    ]
    return render_template("schedule_appointment.html", doctors=doctors)

@app.route("/schedule", methods=["POST"])
def schedule():
    doctor_name = request.form.get("doctor_name")
    specialty = request.form.get("specialty")
    contact = request.form.get("contact")
    building = request.form.get("building")
    address = request.form.get("address")

    return render_template(
        "confirm_appointment.html",
        doctor_name=doctor_name,
        specialty=specialty,
        contact=contact,
        building=building,
        address=address
    )

# Confirming appointment
@app.route('/confirm_appointment')
def confirm_appointment():
    doctor_name = request.args.get('doctor', 'Unknown Doctor')
    return render_template('confirm_appointment.html', doctor_name=doctor_name)

@app.route("/appointment_success", methods=["POST"])
def appointment_success():
    doctor = request.form.get("doctor")
    date = request.form.get("date")
    time = request.form.get("time")
    username = session.get("username", "Anonymous")

    appointment = {
        "patient": username,
        "doctor": doctor,
        "date": date,
        "time": time
    }

    appointments.append(appointment)

    flash(f"Appointment with {doctor} confirmed for {date} at {time}.")
    return render_template("appointment_success.html", doctor=doctor, date=date, time=time)


@app.route("/checkin_success", methods=["POST"])
def checkin_success():
    # You can optionally grab submitted form data if you want:
    patient_name = request.form.get("patient_name")
    appointment_id = request.form.get("appointment_id")

# Flash the success message
    flash(f"Patient {patient_name} (Appointment ID: {appointment_id}) checked in successfully!")

    return render_template("checkin_success.html")

# View appointments
@app.route("/view_appointments")
def view_appointments():
    if "username" in session and session.get("role") == "doctor":
        doctor_name = session["username"]
        doctor_appointments = [appt for appt in appointments if appt["doctor"] == doctor_name]

        # Sort by date and time
        doctor_appointments.sort(key=lambda appt: (appt["date"], appt["time"]))

        return render_template("view_appointments.html", appointments=doctor_appointments)
    else:
        flash("Access denied. Please log in as a doctor.")
        return redirect("/login")

@app.route("/view_all_appointments")
def view_all_appointments():
    if "username" in session and session.get("role") == "frontdesk":
        all_appointments = sorted(enumerate(appointments), key=lambda appt: (appt[1]["date"], appt[1]["time"]))
        return render_template("view_all_appointments.html", appointments=all_appointments)
    else:
        flash("Access denied. Please log in as Front Desk.")
        return redirect("/login")

# Cancel appointments front desk
@app.route("/cancel_appointment/<int:appointment_id>", methods=["POST"])
def cancel_appointment(appointment_id):
    if "username" in session and session.get("role") == "frontdesk":
        try:
            appointments.pop(appointment_id)
            flash("Appointment cancelled successfully.")
        except IndexError:
            flash("Appointment not found.")
        return redirect("/view_all_appointments")
    else:
        flash("Access denied. Please log in as Front Desk.")
        return redirect("/login")

    
# Logout and clear session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
