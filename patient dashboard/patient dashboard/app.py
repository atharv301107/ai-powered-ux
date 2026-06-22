from flask import Flask, render_template, request, jsonify, session
import json, os

app = Flask(__name__)
app.secret_key = 'medicare_secret_key_2025'

# ---- Load patients data ----
DATA_FILE = os.path.join(os.path.dirname(__file__), 'patients_data.json')
with open(DATA_FILE) as f:
    _raw = json.load(f)

# Support both {"users":[...]} and [...] formats
if isinstance(_raw, list):
    patients_data = {"users": _raw}
elif "users" not in _raw:
    # Wrap single patient object
    patients_data = {"users": [_raw]}
else:
    patients_data = _raw

# ---- In-memory data ----
appointments = [
    {"id": 1, "doctor": "Dr. Sneha Kulkarni", "specialty": "Cardiologist",     "date": "2025-06-25", "time": "10:30 AM", "status": "upcoming"},
    {"id": 2, "doctor": "Dr. Ravi Desai",     "specialty": "General Physician", "date": "2025-06-18", "time": "02:00 PM", "status": "completed"},
    {"id": 3, "doctor": "Dr. Meena Joshi",    "specialty": "Dermatologist",     "date": "2025-05-30", "time": "11:00 AM", "status": "completed"},
]

reminders = [
    {"id": 1, "medicine": "Amlodipine 5mg", "time": "08:00 AM", "frequency": "Daily",  "active": True},
    {"id": 2, "medicine": "Vitamin D3",      "time": "01:00 PM", "frequency": "Weekly", "active": True},
    {"id": 3, "medicine": "Aspirin 75mg",    "time": "09:00 PM", "frequency": "Daily",  "active": False},
]

doctors = [
    {"name": "Dr. Sneha Kulkarni", "specialty": "Cardiologist"},
    {"name": "Dr. Ravi Desai",     "specialty": "General Physician"},
    {"name": "Dr. Meena Joshi",    "specialty": "Dermatologist"},
    {"name": "Dr. Amit Shah",      "specialty": "Orthopedic"},
]

# ============================================================
#  AUTH ROUTES
# ============================================================

@app.route('/auth')
def auth_page():
    return render_template('auth.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Please enter username and password.'}), 400

    # Accept any username/password — use entered name as display name
    display_name = username.replace('.', ' ').replace('_', ' ').title()

    session['user_id'] = 1
    session['username'] = username
    session['name'] = display_name

    return jsonify({
        'success': True,
        'user': {
            'id':       1,
            'username': username,
            'name':     display_name,
            'role':     'patient',
        }
    })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# ============================================================
#  MAIN PAGES
# ============================================================

@app.route('/')
def dashboard():
    logged_name = session.get('name', 'Patient')
    logged_username = session.get('username', 'patient')

    # patients_data.json madhla pahila record vapar
    record = patients_data['users'][0] if patients_data.get('users') else {}

    patient = {
        "name": logged_name,
        "username": logged_username,
        "age": record.get("age", "—"),
        "blood_group": record.get("blood_group", "—"),
        "phone": record.get("phone", "—"),
        "email": record.get("email", "—"),
        "address": record.get("address", "—"),
        "doctor": record.get("doctor", "—"),
        "medical_records": record.get("medical_records", [])
    }

    return render_template('dashboard.html', patient=patient, appointments=appointments, reminders=reminders)

@app.route('/appointments')
def appointments_page():
    return render_template('appointments.html', appointments=appointments, doctors=doctors)

@app.route('/reminders')
def reminders_page():
    return render_template('reminders.html', reminders=reminders)

# ============================================================
#  API ENDPOINTS
# ============================================================

@app.route('/api/appointments', methods=['POST'])
def book_appointment():
    data = request.json
    new_appt = {
        "id":       len(appointments) + 1,
        "doctor":   data.get('doctor'),
        "specialty":data.get('specialty', ''),
        "date":     data.get('date'),
        "time":     data.get('time'),
        "status":   "upcoming"
    }
    appointments.append(new_appt)
    return jsonify({'success': True, 'appointment': new_appt})

@app.route('/api/reminders', methods=['POST'])
def add_reminder():
    data = request.json
    new_reminder = {
        "id":        len(reminders) + 1,
        "medicine":  data.get('medicine'),
        "time":      data.get('time'),
        "frequency": data.get('frequency'),
        "active":    True
    }
    reminders.append(new_reminder)
    return jsonify({'success': True, 'reminder': new_reminder})

@app.route('/api/reminders/<int:reminder_id>/toggle', methods=['POST'])
def toggle_reminder(reminder_id):
    for r in reminders:
        if r['id'] == reminder_id:
            r['active'] = not r['active']
            return jsonify({'success': True, 'active': r['active']})
    return jsonify({'success': False}), 404

if __name__ == '__main__':
    app.run(debug=True)