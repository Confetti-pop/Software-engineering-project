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

    user = users.get(username)
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