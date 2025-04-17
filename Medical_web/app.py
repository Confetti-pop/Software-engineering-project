from flask import Flask, render_template, request, redirect, session, url_for
from flask_cors import CORS  # ADD THIS

app = Flask(__name__)
CORS(app, supports_credentials=True)  # MOVE THIS TO ITS OWN LINE

app.secret_key = 'secretkey123'  # needed for session management


# --- Simulated user data ---
users = {
    "patient1": {"password": "pass1", "role": "patient", "name": "Alice Smith"},
    "patient2": {"password": "pass2", "role": "patient", "name": "Bob Jones"},
    "doctor1": {"password": "docpass", "role": "doctor", "name": "Dr. Grey"}
}

# --- Simulated patient records and medications ---
patient_data = {
    "patient1": {
        "name": "Alice Smith",
        "prescriptions": [],
        "appointments": []
    },
    "patient2": {
        "name": "Bob Jones",
        "prescriptions": [],
        "appointments": []
    }
}

medication_store = {
    "Ibuprofen": 10,
    "Amoxicillin": 5
}

# --- Simulated Login Class ---
class Login:
    def __init__(self):
        self.connected = False

    def connectToDatabase(self):
        print("🔌 Connecting to database (simulated)...")
        self.connected = True

    def disconnectDatabase(self):
        print("❌ Disconnecting from database (simulated)...")
        self.connected = False

    def login(self, username, password):
        if not self.connected:
            self.connectToDatabase()

        user = users.get(username)
        if user and user['password'] == password:
            print(f"✅ Login successful for {username}")
            return user
        else:
            print(f"❌ Login failed for {username}")
            return None

# --- Simulated Doctor Class ---
class Doctor:
    def __init__(self, name):
        self.name = name

    def view_patient_records(self):
        print("📄 Viewing all patient records (simulated)")
        return patient_data

    def prescribe_rx(self, patient_id, prescription):
        print(f"💊 Doctor prescribing '{prescription}' to {patient_id}")
        patient_data[patient_id]['prescriptions'].append(prescription)

    def set_appointment(self, patient_id, date):
        print(f"📅 Setting appointment for {patient_id} on {date}")
        patient_data[patient_id]['appointments'].append(date)

    def update_medication_store(self, med_name, quantity):
        print(f"📦 Updating med store: {med_name} → {quantity}")
        medication_store[med_name] = quantity

# --- Routes ---

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        print("📥 GET /login")
        return render_template('login.html')

    print("📥 POST /login received")

    if request.is_json:
        try:
            data = request.get_json(force=True)
            username = data.get('username')
            password = data.get('password')
        except Exception as e:
            print("❌ Error parsing JSON:", e)
            return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"🔐 Form data → Username: {username}, Password: {password}")

    login_manager = Login()
    user = login_manager.login(username, password)
    login_manager.disconnectDatabase()
    if user and user['password'] == password:
        session['username'] = username
        session['role'] = user['role']
        print(f"✅ Logged in: {username} ({user['role']})")

        if request.is_json:
            return jsonify({'success': True, 'role': user['role'], 'name': user['name']})
        else:
            return redirect(url_for('dashboard'))
    else:
        print("❌ Invalid credentials")
        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        else:
            return render_template('login.html', error='Invalid credentials')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['username']
    user = users[user_id]

    if user['role'] == 'doctor':
        doctor = Doctor(user_id)
        records = doctor.view_patient_records()
        return render_template('dashboard_doctor.html', user=user, records=records)

    # ✅ If patient
    patient = patient_data.get(user_id)
    return render_template('dashboard_patient.html', user=user, user_id=user_id, data=patient)
    
@app.route('/doctor/records')
def doctor_records():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    doctor = Doctor(session['username'])
    records = doctor.view_patient_records()
    return render_template('dashboard_doctor.html', records=records, user=users[session['username']])

@app.route('/doctor/prescribe', methods=['POST'])
def prescribe():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    patient_id = request.form['patient_id']
    prescription = request.form['prescription']

    doctor = Doctor(session['username'])
    doctor.prescribe_rx(patient_id, prescription)

    return redirect(url_for('doctor_records'))

@app.route('/doctor/appointment', methods=['POST'])
def set_appointment():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    patient_id = request.form['patient_id']
    date = request.form['appointment_date']

    doctor = Doctor(session['username'])
    doctor.set_appointment(patient_id, date)

    return redirect(url_for('doctor_records'))

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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)