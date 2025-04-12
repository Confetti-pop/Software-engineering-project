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

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users.get(username)
    if user and user['password'] == password:
        session['username'] = username
        session['role'] = user['role']
        return jsonify({'success': True, 'role': user['role'], 'name': user['name']})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = users[session['username']]

    if user['role'] == 'doctor':
        return render_template('dashboard_doctor.html', user=user)
    else:
        return render_template('dashboard_patient.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)