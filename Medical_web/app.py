from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from flask_cors import CORS
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable cross-origin access
app.secret_key = 'secretkey123'       # Required for session tracking
appointments = []                     # In-Memory Appointment Storage 
login_log = []                        # Stores login history
visit_records = []                    # Global list to store recorded patient visits

# --- Simulated user database ---
# username: { password, role, display name }
users = {
    "patient1": {
        "password": "pass1",
        "role": "patient",
        "name": "Alice Smith",
        "phone": "123-456-7890",     
        "address": "123 Main St",
        "appointments": []
    },
    "patient2": {
        "password": "pass2",
        "role": "patient",
        "name": "Bob Jones",
        "phone": "281-445-2890",
        "address": "456 Main st",
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
    },
    "admin1": {
        "password": "adminpass",
        "role": "admin",
        "name": "Administrator"
    },
    "ma1": {
        "password": "mapass",
        "role": "ma",
        "name": "Medical Assistant"
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
        session['name'] = user['name']

        login_log.append({
            "username": username,
            "role": user["role"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Role-based redirection
    if user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user['role'] == 'doctor':
        return redirect(url_for('dashboard_doctor'))
    elif user['role'] == 'frontdesk':
        return redirect(url_for('dashboard_frontdesk'))
    elif user['role'] == 'ma':
        return redirect(url_for('dashboard_ma'))
    elif user['role'] == 'patient':
        return redirect(url_for('dashboard_patient'))
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

# Patient dashboard
@app.route("/dashboard_patient")
def dashboard_patient():
    if "username" not in session:
        return redirect("/login")

    name = session.get("name")
    return render_template("dashboard_patient.html", name=name)


# Doctor dashboard
@app.route("/dashboard_doctor")
def dashboard_doctor():
    if "username" not in session:
        return redirect("/login")
    name = session.get("name")
    return render_template("dashboard_doctor.html", name=name)

# Frontdesk dashboard
@app.route('/dashboard_frontdesk')
def dashboard_frontdesk():
    if "username" not in session:
        return redirect("/login")

    # Example limited patient information for front desk
    patients = [
        {
            "patient_id": "P001",
            "name": "Alice Smith",
            "phone": "832-555-1234",
            "address": "123 Main St, Houston, TX 77001",
            "next_appointment": "05/02/2025 at 10:00 AM"
        },
        {
            "patient_id": "P002",
            "name": "Bob Jones",
            "phone": "832-555-5678",
            "address": "456 Elm St, Houston, TX 77002",
            "next_appointment": "05/03/2025 at 2:00 PM"
        }
    ]

    return render_template('dashboard_frontdesk.html', patients=patients)

# View patient report page
@app.route("/patient_report")
def patient_report():
    if "username" not in session:
        return redirect("/login")
    
    # Example fake patient data
    patient = {
        "name": session.get('name'),
        "dob": "01/15/1995",
        "blood_type": "O+",
        "allergies": "Peanuts",
        "prescriptions": ["Albuterol Inhaler", "Ibuprofen"],
        "last_visit": "04/10/2025"
    }
    
    return render_template("patient_report.html", data=patient)


# Doctor medication inventory page
@app.route('/medication_inventory', methods=['GET', 'POST'])
def medication_inventory():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    doctor = Doctor(session['username'])

    if request.method == 'POST':
        med_name = request.form['med_name']
        quantity = int(request.form['quantity'])
        doctor.update_medication_store(med_name, quantity)

    return render_template('medication_inventory.html', meds=medication_store)

# Prescribe
@app.route('/prescribe_medicine', methods=['GET', 'POST'])
def prescribe_medicine():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        patient_name = request.form.get('patient_name')
        medication = request.form.get('medication')
        dosage = request.form.get('dosage')

        # Save the prescription (for now just flash it or save into a fake list)
        flash(f"Prescribed {medication} ({dosage}) to {patient_name} successfully!")
        return redirect(url_for('prescribe_medicine'))

    return render_template('prescribe_medicine.html')

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

# Check in
@app.route("/patient_checkin")
def patient_checkin():
    return render_template("patient_checkin.html")

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
        doctor_name = users[session["username"]]["name"]  # This gets "Dr. Smith"
        doctor_appointments = [appt for appt in appointments if appt["doctor"] == doctor_name]

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
    
# Medical records
@app.route('/view_medical_record')
def view_medical_record():
    if "username" not in session:
        return redirect("/login")
    
    # Fake patient record info
    record = {
        "name": session.get('name'),
        "dob": "01/15/1995",
        "blood_type": "O+",
        "allergies": "Peanuts, Penicillin",
        "medical_conditions": "Asthma",
        "current_medications": "Albuterol Inhaler",
        "last_visit": "04/10/2025"
    }

    return render_template('view_medical_record.html', record=record)

# Patient reports
@app.route('/view_patient_reports')
def view_patient_reports():
    if "username" not in session:
        return redirect("/login")

    patients = [
        {
            "name": "Alice Smith",
            "dob": "03/12/1995",
            "last_visit": "04/15/2025",
            "medical_conditions": "Asthma",
            "prescriptions": ["Albuterol Inhaler", "Fluticasone"]
        },
        {
            "name": "Bob Jones",
            "dob": "07/22/1992",
            "last_visit": "03/30/2025",
            "medical_conditions": "Hypertension",
            "prescriptions": ["Lisinopril", "Hydrochlorothiazide"]
        }
    ]

    return render_template('view_patient_reports.html', patients=patients)

#Editing patient records
@app.route('/edit_patient_record', methods=['GET', 'POST'])
def edit_patient_record():
    if "username" not in session:
        return redirect("/login")

    # Example: existing patient data
    patient = {
        "name": "Alice Smith",
        "dob": "03/12/1995",
        "medical_conditions": "Asthma",
        "medications": "Albuterol Inhaler, Fluticasone",
        "treatment_plan": "Continue inhaler twice daily."
    }

    if request.method == 'POST':
        # In real project, you'd update the database here!
        patient['medical_conditions'] = request.form['medical_conditions']
        patient['medications'] = request.form['medications']
        patient['treatment_plan'] = request.form['treatment_plan']
        # After saving, you can redirect back to dashboard or show success message
        return render_template('edit_patient_record.html', patient=patient, success=True)

    return render_template('edit_patient_record.html', patient=patient)

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    name = users[session['username']]['name']
    return render_template('admin_dashboard.html', name=name)

# Admin routes
@app.route('/view_users')
def view_users():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    return render_template('view_users.html', users=users)

@app.route('/view_activity_logs')
def view_activity_logs():
    return render_template('view_activity_logs.html')

# Medical Assistant 
@app.route('/dashboard_ma')
def dashboard_ma():
    if 'username' not in session or session['role'] != 'ma':
        return redirect(url_for('login'))
    
    name = users[session['username']]['name']
    return render_template('ma_dashboard.html', name=name)

# Route for medical assistant to record a patient visit
@app.route('/record_visit', methods=['GET', 'POST'])
def record_visit():
    # Restrict access to medical assistants
    if 'username' not in session or session['role'] != 'ma':
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Collect data from form
        patient_name = request.form['patient_name']
        doctor_name = request.form['doctor_name']
        visit_date = request.form['visit_date']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']

        # Store the visit in memory
        visit_records.append({
            "id": len(visit_records),
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "visit_date": visit_date,
            "diagnosis": diagnosis,
            "treatment": treatment,
            "patient_username": patient_name.lower().replace(" ", ""),
            "created_by": session['username']
        })

        flash("Patient visit recorded successfully!")
        return redirect(url_for('dashboard_ma'))

    # Show the form if it's a GET request
    return render_template('record_visit.html')

# MA can view visits 
@app.route('/view_visits')
def view_visits():
    # Allow access to logged-in MAs, doctors, or patients
    if 'username' not in session or session['role'] not in ['ma', 'doctor', 'patient']:
        return redirect(url_for('login'))

    # Show visits depending on role
    if session['role'] == 'patient':
        filtered_visits = [v for v in visit_records if v.get('patient_username') == session['username']]
    elif session['role'] in ['doctor', 'ma']:
        filtered_visits = visit_records
    else:
        return redirect(url_for('login'))

    return render_template('view_visits.html', visits=filtered_visits)

# Part of editing information
@app.route('/edit_visit/<int:visit_id>', methods=['GET', 'POST'])
def edit_visit(visit_id):
    if 'username' not in session or session['role'] != 'ma':
        return redirect(url_for('login'))

    visit = next((v for v in visit_records if v['id'] == visit_id), None)
    if not visit:
        flash("Visit not found.")
        return redirect(url_for('view_visits'))

    if request.method == 'POST':
        # Update visit info with new values
        visit['patient_name'] = request.form['patient_name']
        visit['doctor_name'] = request.form['doctor_name']
        visit['visit_date'] = request.form['visit_date']
        visit['diagnosis'] = request.form['diagnosis']
        visit['treatment'] = request.form['treatment']
        flash("Visit updated successfully!")
        return redirect(url_for('view_visits'))

    return render_template('edit_visit.html', visit=visit)

# Deleting past information
@app.route('/delete_visit/<int:visit_id>', methods=['POST'])
def delete_visit(visit_id):
    if 'username' not in session or session['role'] != 'ma':
        return redirect(url_for('login'))

    global visit_records
    # Filter out the visit with the matching ID
    visit_records = [v for v in visit_records if v['id'] != visit_id]
    flash("Visit deleted successfully.")
    return redirect(url_for('view_visits'))

# Viewing history
@app.route('/ma/view_history', methods=['GET', 'POST'])
def view_medical_history():
    if 'username' not in session or session['role'] != 'ma':
        return redirect(url_for('login'))

    filtered_visits = visit_records  # start with all visits

    if request.method == 'POST':
        search_name = request.form.get('patient_name', '').lower()
        search_date = request.form.get('visit_date', '')

        # Filter by name and/or date
        filtered_visits = [
            visit for visit in visit_records
            if (search_name in visit['patient_name'].lower()) and
               (search_date in visit['date'])
        ]

    return render_template('view_history.html', visits=filtered_visits)

# Patient medical history
@app.route('/patient_medical_history')
def patient_medical_history():
    if 'username' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))

    username = session['username']
    # Filter only that patient’s visits
    patient_visits = [v for v in visit_records if v['patient_username'] == username]
    return render_template('patient_medical_history.html', visits=patient_visits)

# Display dropdown to select patient
@app.route('/select_patient_history')
def select_patient_history():
    if 'username' not in session or session['role'] not in ['doctor', 'ma']:
        return redirect(url_for('login'))
    
    # Get all patient usernames
    patient_list = {k: v['name'] for k, v in users.items() if v['role'] == 'patient'}
    return render_template('select_patient_history.html', patients=patient_list)

# Handle patient selection and show history
@app.route('/view_patient_history', methods=['POST'])
def view_patient_history():
    if 'username' not in session or session['role'] not in ['doctor', 'ma']:
        return redirect(url_for('login'))

    patient_id = request.form.get('patient_id')
    visits = [v for v in visit_records if v['patient_id'] == patient_id]
    
    return render_template('patient_history_doctor_ma.html', visits=visits)

# Edit Appointment Route
@app.route("/edit_appointment/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    if "username" not in session or session.get("role") != "frontdesk":
        flash("Access denied. Please log in as Front Desk.")
        return redirect("/login")

    try:
        # Fetch the selected appointment
        appointment = appointments[appointment_id]
    except IndexError:
        flash("Appointment not found.")
        return redirect("/view_all_appointments")

    if request.method == "POST":
        # Get updated data from the form
        new_date = request.form.get("date")
        new_time = request.form.get("time")
        new_doctor = request.form.get("doctor")

        # Update appointment values
        appointment["date"] = new_date
        appointment["time"] = new_time
        appointment["doctor"] = new_doctor

        flash("Appointment updated successfully.")
        return redirect("/view_all_appointments")

    return render_template("edit_appointment.html", appointment=appointment, appointment_id=appointment_id)

# Route for patients to update their personal info
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    # Check if user is logged in and is a patient
    if 'username' not in session or session['role'] != 'patient':
        flash("Access denied. Please log in as a patient.")
        return redirect(url_for('login'))

    username = session['username']
    user = users[username]

    if request.method == 'POST':
        # Update only editable fields
        user['name'] = request.form['name']
        user['phone'] = request.form['phone']
        user['address'] = request.form['address']
        flash("Profile updated successfully.")
        return redirect(url_for('dashboard_patient'))  # Redirect after save

    return render_template('edit_profile.html', user=user)

# View profile
@app.route("/view_profile")
def view_profile():
    if "username" not in session or session["role"] != "patient":
        flash("Access denied. Please log in as a patient.")
        return redirect("/login")
    
    user = users[session["username"]]
    return render_template("view_profile.html", user=user)


# Logout and clear session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
