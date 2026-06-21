from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
from datetime import date
import json, os

def load_env():
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    import secrets
    app.secret_key = secrets.token_hex(24)
DB_PATH = Path(__file__).parent / "healthcare.db"

# Doctor profiles detail dictionary
DOCTOR_DETAILS = {
    "Dr. Sneha Patil": {
        "qualification": "MD, DM (Cardiology)",
        "specialization": "Interventional Cardiology",
        "experience": "14 Years",
        "availability": "Mon - Fri (10:00 AM - 04:00 PM)",
        "photo": "doc_sneha.jpg",
        "department": "Cardiology",
        "rating": "4.9★"
    },
    "Dr. Mehta": {
        "qualification": "BDS, MDS (Orthodontics)",
        "specialization": "Dental & Facial Orthopedics",
        "experience": "10 Years",
        "availability": "Mon - Sat (09:00 AM - 01:00 PM)",
        "photo": "doc_mehta.jpg",
        "department": "Radiology",
        "rating": "4.8★"
    },
    "Dr. Khan": {
        "qualification": "MS (Orthopedics)",
        "specialization": "Joint Replacement & Spine Surgery",
        "experience": "12 Years",
        "availability": "Tue, Thu, Sat (02:00 PM - 06:00 PM)",
        "photo": "doc_khan.jpg",
        "department": "Orthopedics",
        "rating": "4.7★"
    },
    "Dr. Patil": {
        "qualification": "MBBS, MD (General Medicine)",
        "specialization": "Internal Medicine & Diabetology",
        "experience": "16 Years",
        "availability": "Daily (08:00 AM - 12:00 PM)",
        "photo": "doc_patil.jpg",
        "department": "General Medicine",
        "rating": "4.9★"
    },
    "Dr. Sarah D'Souza": {
        "qualification": "MD (Pediatrics), DCH",
        "specialization": "Neonatology & Pediatric Care",
        "experience": "8 Years",
        "availability": "Mon - Fri (11:00 AM - 03:00 PM)",
        "photo": "doc_sarah.jpg",
        "department": "Pediatrics",
        "rating": "4.8★"
    },
    "Dr. Priya Sharma": {
        "qualification": "MD (Dermatology)",
        "specialization": "Cosmetology & Clinical Dermatology",
        "experience": "9 Years",
        "availability": "Mon, Wed, Fri (04:00 PM - 07:00 PM)",
        "photo": "doc_priya.jpg",
        "department": "Dermatology",
        "rating": "4.7★"
    },
    "Dr. Rajesh Iyer": {
        "qualification": "MD, DM (Neurology)",
        "specialization": "Stroke & Neuromuscular Disorders",
        "experience": "15 Years",
        "availability": "Tue, Thu (10:00 AM - 02:00 PM)",
        "photo": "doc_rajesh.jpg",
        "department": "Neurology",
        "rating": "4.9★"
    },
    "Dr. Vikram Sinha": {
        "qualification": "MS (ENT)",
        "specialization": "Otology & Skull Base Surgery",
        "experience": "11 Years",
        "availability": "Daily (01:00 PM - 04:00 PM)",
        "photo": "doc_vikram.jpg",
        "department": "ENT",
        "rating": "4.6★"
    },
    "Dr. Anjali Desai": {
        "qualification": "MD, DGO (Gynecology)",
        "specialization": "High-Risk Obstetrics & Gynae-Oncology",
        "experience": "13 Years",
        "availability": "Mon - Sat (10:00 AM - 01:00 PM)",
        "photo": "doc_anjali.jpg",
        "department": "Gynecology",
        "rating": "4.9★"
    },
    "Dr. Sanjay Kapoor": {
        "qualification": "MD (Emergency Medicine)",
        "specialization": "Trauma & Critical Care Specialist",
        "experience": "10 Years",
        "availability": "24/7 Rotational",
        "photo": "doc_sanjay.jpg",
        "department": "Emergency Care",
        "rating": "4.8★"
    }
}


# ─────────────────────────────────────────────
#  DATABASE HELPERS
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        email       TEXT    UNIQUE NOT NULL,
        password    TEXT    NOT NULL,
        role        TEXT    NOT NULL,
        status      TEXT    NOT NULL DEFAULT 'Active',
        created_at  TEXT    NOT NULL
    );
    CREATE TABLE IF NOT EXISTS appointments (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name      TEXT NOT NULL,
        doctor_name       TEXT NOT NULL,
        appointment_date  TEXT NOT NULL,
        department        TEXT NOT NULL,
        status            TEXT NOT NULL DEFAULT 'Pending',
        time              TEXT NOT NULL DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS health_stats (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        stat_date           TEXT NOT NULL,
        patients_count      INTEGER NOT NULL,
        doctors_count       INTEGER NOT NULL,
        appointments_count  INTEGER NOT NULL,
        emergency_cases     INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS reminders (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL,
        medicine    TEXT    NOT NULL,
        time        TEXT    NOT NULL,
        frequency   TEXT    NOT NULL,
        active      INTEGER NOT NULL DEFAULT 1
    );
    """)

    # ── seed default users ──
    seed_users = [
        ("Admin User",        "demoadmin@healthcare.com",   generate_password_hash("demo123"),   "Admin",   "Active"),
        ("Dr. Sneha Patil",   "demodoctor@healthcare.com",  generate_password_hash("demo123"),  "Doctor",  "Active"),
        ("Rahul Patil",       "patient@healthcare.com",     generate_password_hash("patient123"), "Patient", "Active"),
        ("Dr. Mehta",         "mehta@healthcare.com",       generate_password_hash("doctor123"),  "Doctor",  "Active"),
        ("Dr. Khan",          "khan@healthcare.com",        generate_password_hash("doctor123"),  "Doctor",  "Active"),
        ("Dr. Patil",         "patil@healthcare.com",       generate_password_hash("doctor123"),  "Doctor",  "Active"),
        ("Dr. Sarah D'Souza", "sarah@healthcare.com",       generate_password_hash("doctor123"),  "Doctor",  "Active"),
        ("Dr. Priya Sharma",  "priya@healthcare.com",       generate_password_hash("doctor123"),  "Doctor",  "Active"),
        ("Dr. Rajesh Iyer",   "rajesh@healthcare.com",      generate_password_hash("doctor123"),  "Doctor",  "Active"),
        ("Dr. Vikram Sinha",  "vikram@healthcare.com",      generate_password_hash("doctor123"),  "Doctor",  "Active"),
        ("Dr. Anjali Desai",  "desai@healthcare.com",       generate_password_hash("doctor123"),  "Doctor",  "Active"),
        ("Dr. Sanjay Kapoor", "kapoor@healthcare.com",      generate_password_hash("doctor123"),  "Doctor",  "Active"),
    ]
    for name, email, pw, role, status in seed_users:
        if not cur.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            cur.execute(
                "INSERT INTO users(name,email,password,role,status,created_at) VALUES(?,?,?,?,?,?)",
                (name, email, pw, role, status, str(date.today())),
            )

    # ── seed appointments ──
    if cur.execute("SELECT COUNT(*) AS c FROM appointments").fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO appointments(patient_name,doctor_name,appointment_date,department,status,time) VALUES(?,?,?,?,?,?)",
            [
                ("Amit Kadam",   "Dr. Sneha Patil", "2026-06-16", "Cardiology",  "Confirmed", "10:30 AM"),
                ("Priya Jadhav", "Dr. Mehta",       "2026-06-17", "Dental",      "Pending",   "02:00 PM"),
                ("Rohit Mali",   "Dr. Khan",        "2026-06-18", "Orthopedic",  "Completed", "11:00 AM"),
                ("Neha Pawar",   "Dr. Patil",       "2026-06-19", "General",     "Cancelled", "09:00 AM"),
                ("Rahul Patil",  "Dr. Sneha Patil", "2026-07-05", "Cardiology",  "Upcoming",  "10:30 AM"),
                ("Sunita More",  "Dr. Khan",        "2026-07-08", "Orthopedic",  "Pending",   "03:00 PM"),
            ],
        )

    # ── seed health stats ──
    if cur.execute("SELECT COUNT(*) AS c FROM health_stats").fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO health_stats(stat_date,patients_count,doctors_count,appointments_count,emergency_cases) VALUES(?,?,?,?,?)",
            [
                ("2026-06-14", 120, 15, 38, 4),
                ("2026-06-15", 145, 16, 45, 6),
                ("2026-06-16", 160, 16, 52, 8),
                ("2026-06-17", 132, 17, 41, 5),
                ("2026-06-18", 175, 17, 59, 9),
                ("2026-06-19", 188, 18, 63, 7),
                ("2026-06-20", 201, 18, 70, 11),
            ],
        )

    # ── seed reminders for patient ──
    patient = cur.execute("SELECT id FROM users WHERE role='Patient' LIMIT 1").fetchone()
    if patient and cur.execute("SELECT COUNT(*) AS c FROM reminders WHERE user_id=?", (patient["id"],)).fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO reminders(user_id,medicine,time,frequency,active) VALUES(?,?,?,?,?)",
            [
                (patient["id"], "Amlodipine 5mg", "08:00 AM", "Daily",  1),
                (patient["id"], "Vitamin D3",     "01:00 PM", "Weekly", 1),
                (patient["id"], "Aspirin 75mg",   "09:00 PM", "Daily",  0),
            ],
        )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def get_current_user():
    if "user_id" not in session:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    conn.close()
    return user


def require_role(*roles):
    user = get_current_user()
    if not user or user["role"] not in roles:
        flash("Access Denied", "danger")
        return redirect(url_for("dashboard"))
    return None


# ─────────────────────────────────────────────
#  AUTH MIDDLEWARE
# ─────────────────────────────────────────────
PUBLIC_ROUTES = {"login", "logout", "static", "landing", "about", "departments", "doctors", "packages", "emergency", "contact", "book_appointment", "signup"}


@app.before_request
def require_login():
    if request.endpoint not in PUBLIC_ROUTES and "user_id" not in session:
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Authentication required."}), 401
        return redirect(url_for("login"))


# ─────────────────────────────────────────────────
#  PUBLIC WEBSITE PAGES
# ─────────────────────────────────────────────────
@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/departments")
def departments():
    return render_template("departments.html")


@app.route("/doctors")
def doctors():
    conn = get_db()
    doctors_list = conn.execute("SELECT * FROM users WHERE role='Doctor' AND status='Active'").fetchall()
    conn.close()
    
    processed_docs = []
    for d in doctors_list:
        info = DOCTOR_DETAILS.get(d["name"], {
            "qualification": "MBBS, MD",
            "specialization": "Consultant Specialist",
            "experience": "8 Years",
            "availability": "Mon - Sat (10:00 AM - 05:00 PM)",
            "photo": "default_doc.jpg",
            "department": "General Medicine",
            "rating": "4.8★"
        })
        processed_docs.append({
            "name": d["name"],
            "email": d["email"],
            "qualification": info["qualification"],
            "specialization": info["specialization"],
            "experience": info["experience"],
            "availability": info["availability"],
            "photo": info["photo"],
            "department": info["department"],
            "rating": info["rating"]
        })
        
    search = request.args.get("search", "").strip().lower()
    dept_filter = request.args.get("department", "").strip()
    
    if search:
        processed_docs = [d for d in processed_docs if search in d["name"].lower() or search in d["specialization"].lower()]
    if dept_filter:
        processed_docs = [d for d in processed_docs if d["department"].lower() == dept_filter.lower()]
        
    return render_template("doctors.html", doctors=processed_docs, search=search, department=dept_filter)


@app.route("/packages")
def packages():
    return render_template("packages.html")


@app.route("/emergency")
def emergency():
    return render_template("emergency.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thank you for contacting SmartCare Hospital. We will reach back to you shortly.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/book-appointment", methods=["GET", "POST"])
def book_appointment():
    conn = get_db()
    doctors_list = conn.execute("SELECT * FROM users WHERE role='Doctor' AND status='Active'").fetchall()
    conn.close()
    
    processed_docs = []
    for d in doctors_list:
        info = DOCTOR_DETAILS.get(d["name"], {"department": "General Medicine"})
        processed_docs.append({"name": d["name"], "department": info["department"]})
        
    if request.method == "POST":
        patient_name = request.form.get("patient_name")
        doctor_name = request.form.get("doctor_name")
        appointment_date = request.form.get("appointment_date")
        department = request.form.get("department")
        time_slot = request.form.get("time")
        
        conn = get_db()
        conn.execute(
            "INSERT INTO appointments(patient_name,doctor_name,appointment_date,department,status,time) VALUES(?,?,?,?,?,?)",
            (patient_name, doctor_name, appointment_date, department, "Pending", time_slot)
        )
        conn.commit()
        conn.close()
        flash(f"Appointment request submitted successfully! Status: Pending review.", "success")
        return redirect(url_for("book_appointment"))
        
    return render_template("book_appointment.html", doctors=processed_docs)


# ─────────────────────────────────────────────────
#  AUTH ROUTES
# ─────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email_or_username = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        conn     = get_db()
        
        # Look up by email exactly, or check email prefix/name if input has no domain
        if "@" in email_or_username:
            user = conn.execute("SELECT * FROM users WHERE email=?", (email_or_username,)).fetchone()
        else:
            user = conn.execute("SELECT * FROM users WHERE email=? OR email LIKE ? OR name=?", 
                                (email_or_username, email_or_username + "@%", email_or_username)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"]    = user["id"]
            session["user_name"]  = user["name"]
            session["user_role"]  = user["role"]
            session["user_email"] = user["email"]
            flash(f"Welcome back, {user['name']}! 👋", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Successfully Logged Out", "success")
    return redirect(url_for("landing"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Real-time backend validation
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("signup.html")

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("An account with this email already exists.", "danger")
            return render_template("signup.html")

        try:
            hashed_pw = generate_password_hash(password)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users(name,email,password,role,status,created_at) VALUES(?,?,?,?,?,?)",
                (name, email, hashed_pw, "Patient", "Active", str(date.today()))
            )
            user_id = cur.lastrowid
            conn.commit()
            conn.close()

            # Write metadata to patients_data.json
            data_file = os.path.join(os.path.dirname(__file__), "patients_data.json")
            pdata = {"users": []}
            if os.path.exists(data_file):
                with open(data_file) as f:
                    try:
                        pdata = json.load(f)
                    except:
                        pass
            
            age = 30
            try:
                from datetime import datetime
                dob_d = datetime.strptime(dob, "%Y-%m-%d")
                today = date.today()
                age = today.year - dob_d.year - ((today.month, today.day) < (dob_d.month, dob_d.day))
            except:
                pass

            new_patient = {
                "id": user_id,
                "username": email.split("@")[0],
                "name": name,
                "role": "patient",
                "age": age,
                "blood_group": "—",
                "phone": phone,
                "email": email,
                "address": "—",
                "gender": gender,
                "doctor": "Dr. Sneha Patil",
                "medical_records": []
            }
            pdata.setdefault("users", []).append(new_patient)
            with open(data_file, "w") as f:
                json.dump(pdata, f, indent=2)

            flash("Account created successfully! Please sign in.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash("An error occurred during registration. Please try again.", "danger")
            print(f"Signup error: {e}")

    return render_template("signup.html")


# ─────────────────────────────────────────────
#  DASHBOARD HUB
# ─────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    role_map = {"Admin": "admin_dashboard", "Patient": "patient_dashboard", "Doctor": "doctor_dashboard"}
    return redirect(url_for(role_map.get(user["role"], "dashboard_home")))


@app.route("/home")
def dashboard_home():
    user = get_current_user()
    conn = get_db()
    stats = {
        "total_users":        conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"],
        "total_doctors":      conn.execute("SELECT COUNT(*) AS c FROM users WHERE role='Doctor'").fetchone()["c"],
        "total_patients":     conn.execute("SELECT COUNT(*) AS c FROM users WHERE role='Patient'").fetchone()["c"],
        "total_appointments": conn.execute("SELECT COUNT(*) AS c FROM appointments").fetchone()["c"],
    }
    conn.close()
    return render_template("dashboard_home.html", user=user, stats=stats)


# ─────────────────────────────────────────────
#  ADMIN ROUTES
# ─────────────────────────────────────────────
@app.route("/admin")
def admin_dashboard():
    user = get_current_user()
    if user["role"] != "Admin":
        flash("Access Denied", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db()
    total_users        = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    total_doctors      = conn.execute("SELECT COUNT(*) AS c FROM users WHERE role='Doctor'").fetchone()["c"]
    total_patients     = conn.execute("SELECT COUNT(*) AS c FROM users WHERE role='Patient'").fetchone()["c"]
    total_appointments = conn.execute("SELECT COUNT(*) AS c FROM appointments").fetchone()["c"]
    pending_appointments = conn.execute("SELECT COUNT(*) AS c FROM appointments WHERE status='Pending'").fetchone()["c"]

    role_rows        = conn.execute("SELECT role, COUNT(*) AS total FROM users GROUP BY role").fetchall()
    appointment_rows = conn.execute("SELECT status, COUNT(*) AS total FROM appointments GROUP BY status").fetchall()
    recent_appointments = conn.execute("SELECT * FROM appointments ORDER BY appointment_date DESC LIMIT 5").fetchall()
    latest_stats     = list(reversed(conn.execute("SELECT * FROM health_stats ORDER BY stat_date DESC LIMIT 7").fetchall()))
    
    # Department stats (count from appointments grouped by department)
    dept_rows = conn.execute("SELECT department, COUNT(*) AS total FROM appointments GROUP BY department").fetchall()
    conn.close()

    revenue_total = total_appointments * 500 + 15200  # Seeding standard baseline revenue
    revenue_monthly = (total_appointments - pending_appointments) * 500 + pending_appointments * 100 + 3800
    
    dept_labels = [d["department"] for d in dept_rows] if dept_rows else ["General", "Cardiology", "Orthopedics"]
    dept_data = [d["total"] for d in dept_rows] if dept_rows else [10, 5, 2]

    # Activity logs
    activity_logs = [
        {"timestamp": "10 mins ago", "action": "Admin User updated Dr. Sneha Patil's shift schedule."},
        {"timestamp": "45 mins ago", "action": "System processed appointment request #294 for Cardiology."},
        {"timestamp": "2 hours ago", "action": "New patient Rahul Patil completed self-registration details."},
        {"timestamp": "5 hours ago", "action": "Log cleanup task successfully synchronized database schemas."}
    ]

    return render_template(
        "admin_dashboard.html",
        user=user,
        total_users=total_users, total_doctors=total_doctors,
        total_patients=total_patients, total_appointments=total_appointments,
        pending_appointments=pending_appointments,
        role_labels=[r["role"] for r in role_rows],
        role_data=[r["total"] for r in role_rows],
        appointment_labels=[r["status"] for r in appointment_rows],
        appointment_data=[r["total"] for r in appointment_rows],
        recent_appointments=recent_appointments,
        stat_dates=[r["stat_date"] for r in latest_stats],
        patient_counts=[r["patients_count"] for r in latest_stats],
        emergency_counts=[r["emergency_cases"] for r in latest_stats],
        revenue_total=revenue_total,
        revenue_monthly=revenue_monthly,
        dept_labels=dept_labels,
        dept_data=dept_data,
        activity_logs=activity_logs
    )


@app.route("/admin/users")
def admin_users():
    res = require_role("Admin")
    if res: return res
    user = get_current_user()
    search      = request.args.get("search", "")
    role_filter = request.args.get("role", "")
    query       = "SELECT * FROM users WHERE 1=1"
    params      = []
    if search:
        query  += " AND (name LIKE ? OR email LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if role_filter:
        query  += " AND role=?"
        params.append(role_filter)
    query += " ORDER BY id DESC"
    conn      = get_db()
    user_list = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("users.html", user=user, users=user_list, search=search, role=role_filter)


@app.route("/admin/users/add", methods=["GET", "POST"])
def add_user():
    res = require_role("Admin")
    if res: return res
    user = get_current_user()
    if request.method == "POST":
        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users(name,email,password,role,status,created_at) VALUES(?,?,?,?,?,?)",
                (request.form["name"], request.form["email"],
                 generate_password_hash(request.form["password"]),
                 request.form["role"], request.form["status"], str(date.today())),
            )
            conn.commit()
            conn.close()
            flash("User added successfully", "success")
            return redirect(url_for("admin_users"))
        except sqlite3.IntegrityError:
            flash("Email already exists", "danger")
    return render_template("user_form.html", user=user, title="Add User", edit_user=None)


@app.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    res = require_role("Admin")
    if res: return res
    user     = get_current_user()
    conn     = get_db()
    edit_obj = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if request.method == "POST":
        pw = request.form.get("password", "")
        if pw:
            conn.execute("UPDATE users SET name=?,email=?,password=?,role=?,status=? WHERE id=?",
                         (request.form["name"], request.form["email"], generate_password_hash(pw),
                          request.form["role"], request.form["status"], user_id))
        else:
            conn.execute("UPDATE users SET name=?,email=?,role=?,status=? WHERE id=?",
                         (request.form["name"], request.form["email"],
                          request.form["role"], request.form["status"], user_id))
        conn.commit()
        conn.close()
        flash("User updated successfully", "success")
        return redirect(url_for("admin_users"))
    conn.close()
    return render_template("user_form.html", user=user, title="Edit User", edit_user=edit_obj)


@app.route("/admin/users/delete/<int:user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    res = require_role("Admin")
    if res: return res
    if session.get("user_id") == user_id:
        flash("You cannot delete your own account", "warning")
        return redirect(url_for("admin_users"))
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    flash("User deleted successfully", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/appointments")
def admin_appointments():
    res = require_role("Admin")
    if res: return res
    user          = get_current_user()
    status_filter = request.args.get("status", "")
    query         = "SELECT * FROM appointments WHERE 1=1"
    params        = []
    if status_filter:
        query += " AND status=?"
        params.append(status_filter)
    query += " ORDER BY appointment_date DESC"
    conn              = get_db()
    appointment_list  = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("admin_appointments.html", user=user, appointments=appointment_list, status=status_filter)


@app.route("/admin/appointments/add", methods=["GET", "POST"])
def add_appointment():
    res = require_role("Admin")
    if res: return res
    user = get_current_user()
    if request.method == "POST":
        conn = get_db()
        conn.execute(
            "INSERT INTO appointments(patient_name,doctor_name,appointment_date,department,status,time) VALUES(?,?,?,?,?,?)",
            (request.form["patient_name"], request.form["doctor_name"],
             request.form["appointment_date"], request.form["department"],
             request.form["status"], request.form.get("time", "")),
        )
        conn.commit()
        conn.close()
        flash("Appointment added successfully", "success")
        return redirect(url_for("admin_appointments"))
    return render_template("appointment_form.html", user=user, title="Add Appointment", appointment=None)


@app.route("/admin/appointments/edit/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    res = require_role("Admin")
    if res: return res
    user = get_current_user()
    conn = get_db()
    appt = conn.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()
    if request.method == "POST":
        conn.execute(
            "UPDATE appointments SET patient_name=?,doctor_name=?,appointment_date=?,department=?,status=?,time=? WHERE id=?",
            (request.form["patient_name"], request.form["doctor_name"],
             request.form["appointment_date"], request.form["department"],
             request.form["status"], request.form.get("time", ""), appointment_id),
        )
        conn.commit()
        conn.close()
        flash("Appointment updated", "success")
        return redirect(url_for("admin_appointments"))
    conn.close()
    return render_template("appointment_form.html", user=user, title="Edit Appointment", appointment=appt)


@app.route("/admin/appointments/delete/<int:appointment_id>", methods=["GET", "POST"])
def delete_appointment(appointment_id):
    res = require_role("Admin")
    if res: return res
    conn = get_db()
    conn.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
    conn.commit()
    conn.close()
    flash("Appointment deleted", "success")
    return redirect(url_for("admin_appointments"))


@app.route("/admin/health-stats", methods=["GET", "POST"])
def health_stats():
    res = require_role("Admin")
    if res: return res
    user = get_current_user()
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO health_stats(stat_date,patients_count,doctors_count,appointments_count,emergency_cases) VALUES(?,?,?,?,?)",
            (request.form["stat_date"], request.form["patients_count"],
             request.form["doctors_count"], request.form["appointments_count"],
             request.form["emergency_cases"]),
        )
        conn.commit()
        flash("Health statistics saved", "success")
        return redirect(url_for("health_stats"))
    stats = conn.execute("SELECT * FROM health_stats ORDER BY stat_date DESC").fetchall()
    conn.close()
    return render_template("health_stats.html", user=user, stats=stats)


@app.route("/admin/health-stats/delete/<int:stat_id>", methods=["GET", "POST"])
def delete_health_stat(stat_id):
    res = require_role("Admin")
    if res: return res
    conn = get_db()
    conn.execute("DELETE FROM health_stats WHERE id=?", (stat_id,))
    conn.commit()
    conn.close()
    flash("Health statistic deleted", "success")
    return redirect(url_for("health_stats"))


# ─────────────────────────────────────────────
#  PATIENT ROUTES
# ─────────────────────────────────────────────
def _load_patient_extras(email):
    data_file = os.path.join(os.path.dirname(__file__), "patients_data.json")
    if os.path.exists(data_file):
        with open(data_file) as f:
            pdata = json.load(f)
        users_list = pdata.get("users", [])
        for u in users_list:
            if u.get("email") == email:
                return u
        return users_list[0] if users_list else {}
    return {}


@app.route("/patient")
def patient_dashboard():
    res = require_role("Patient")
    if res: return res
    user  = get_current_user()
    conn  = get_db()
    appts = conn.execute("SELECT * FROM appointments WHERE patient_name=? ORDER BY appointment_date DESC", (user["name"],)).fetchall()
    rems  = conn.execute("SELECT * FROM reminders WHERE user_id=?", (user["id"],)).fetchall()
    conn.close()

    rec    = _load_patient_extras(user["email"])
    patient = {
        "name":           user["name"],
        "email":          user["email"],
        "age":            rec.get("age", "—"),
        "blood_group":    rec.get("blood_group", "—"),
        "phone":          rec.get("phone", "—"),
        "address":        rec.get("address", "—"),
        "doctor":         rec.get("doctor", "—"),
        "medical_records":rec.get("medical_records", []),
    }
    upcoming  = [a for a in appts if a["status"] in ("Upcoming", "Confirmed", "Pending")]
    completed = [a for a in appts if a["status"] == "Completed"]

    return render_template(
        "patient_dashboard.html",
        user=user, patient=patient,
        appointments=appts, reminders=rems,
        upcoming=upcoming, completed=completed,
    )


@app.route("/patient/appointments", methods=["GET", "POST"])
def patient_appointments():
    res = require_role("Patient")
    if res: return res
    user = get_current_user()
    if request.method == "POST":
        doctor_name      = request.form.get("doctor_name")
        appointment_date = request.form.get("appointment_date")
        department       = request.form.get("department", "General")
        time_slot        = request.form.get("time", "")
        
        conn = get_db()
        conn.execute(
            "INSERT INTO appointments(patient_name,doctor_name,appointment_date,department,status,time) VALUES(?,?,?,?,?,?)",
            (user["name"], doctor_name, appointment_date, department, "Upcoming", time_slot)
        )
        conn.commit()
        conn.close()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("patient_appointments"))

    conn    = get_db()
    doctors = conn.execute("SELECT * FROM users WHERE role='Doctor'").fetchall()
    appts   = conn.execute("SELECT * FROM appointments WHERE patient_name=? ORDER BY appointment_date DESC", (user["name"],)).fetchall()
    conn.close()
    return render_template("patient_appointments.html", user=user, appointments=appts, doctors=doctors)


@app.route("/patient/reminders", methods=["GET", "POST"])
def patient_reminders():
    res = require_role("Patient")
    if res: return res
    user = get_current_user()
    if request.method == "POST":
        medicine  = request.form.get("medicine")
        time      = request.form.get("time")
        frequency = request.form.get("frequency", "Daily")
        
        conn = get_db()
        conn.execute(
            "INSERT INTO reminders(user_id,medicine,time,frequency,active) VALUES(?,?,?,?,?)",
            (user["id"], medicine, time, frequency, 1)
        )
        conn.commit()
        conn.close()
        flash("Medication reminder added successfully!", "success")
        return redirect(url_for("patient_reminders"))

    conn = get_db()
    rems = conn.execute("SELECT * FROM reminders WHERE user_id=?", (user["id"],)).fetchall()
    conn.close()
    return render_template("patient_reminders.html", user=user, reminders=rems)


# ── Patient API ──
@app.route("/api/appointments", methods=["POST"])
def api_book_appointment():
    user = get_current_user()
    data = request.json or {}
    conn = get_db()
    conn.execute(
        "INSERT INTO appointments(patient_name,doctor_name,appointment_date,department,status,time) VALUES(?,?,?,?,?,?)",
        (user["name"], data.get("doctor", ""), data.get("date", ""),
         data.get("specialty", "General"), "Upcoming", data.get("time", "")),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/reminders", methods=["POST"])
def api_add_reminder():
    user = get_current_user()
    data = request.json or {}
    conn = get_db()
    conn.execute(
        "INSERT INTO reminders(user_id,medicine,time,frequency,active) VALUES(?,?,?,?,?)",
        (user["id"], data.get("medicine", ""), data.get("time", ""), data.get("frequency", "Daily"), 1),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/reminders/<int:reminder_id>/toggle", methods=["POST"])
def api_toggle_reminder(reminder_id):
    conn = get_db()
    rem  = conn.execute("SELECT * FROM reminders WHERE id=?", (reminder_id,)).fetchone()
    if rem:
        new_active = 0 if rem["active"] else 1
        conn.execute("UPDATE reminders SET active=? WHERE id=?", (new_active, reminder_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "active": bool(new_active)})
    conn.close()
    return jsonify({"success": False}), 404


@app.route("/patient/reminders/delete/<int:rem_id>", methods=["GET", "POST"])
def delete_reminder(rem_id):
    res = require_role("Patient")
    if res: return res
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("DELETE FROM reminders WHERE id=? AND user_id=?", (rem_id, user["id"]))
    conn.commit()
    conn.close()
    flash("Reminder deleted successfully", "success")
    return redirect(url_for("patient_reminders"))


# ─────────────────────────────────────────────
#  DOCTOR ROUTES
# ─────────────────────────────────────────────
@app.route("/doctor")
def doctor_dashboard():
    res = require_role("Doctor")
    if res: return res
    user  = get_current_user()
    conn  = get_db()
    appts = conn.execute("SELECT * FROM appointments WHERE doctor_name=? ORDER BY appointment_date DESC", (user["name"],)).fetchall()
    patients_list = conn.execute("SELECT * FROM users WHERE role='Patient'").fetchall()
    total_patients = len(patients_list)
    pending  = conn.execute("SELECT COUNT(*) AS c FROM appointments WHERE doctor_name=? AND status='Pending'", (user["name"],)).fetchone()["c"]
    confirmed= conn.execute("SELECT COUNT(*) AS c FROM appointments WHERE doctor_name=? AND status='Confirmed'", (user["name"],)).fetchone()["c"]
    completed= conn.execute("SELECT COUNT(*) AS c FROM appointments WHERE doctor_name=? AND status='Completed'", (user["name"],)).fetchone()["c"]
    conn.close()
    return render_template(
        "doctor_dashboard.html",
        user=user, appointments=appts, patients=patients_list,
        total_patients=total_patients, pending=pending,
        confirmed=confirmed, completed=completed,
    )


@app.route("/api/appointments/<int:appt_id>/status", methods=["POST"])
def update_appt_status(appt_id):
    data   = request.json or {}
    status = data.get("status", "Pending")
    conn   = get_db()
    conn.execute("UPDATE appointments SET status=? WHERE id=?", (status, appt_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ─────────────────────────────────────────────
#  CHATBOT
# ─────────────────────────────────────────────
@app.route("/chatbot")
def chatbot():
    return redirect(url_for("dashboard"))


@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "Unauthorized access denied."}), 401
        
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"success": False, "error": "Message content is empty."}), 400
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"success": False, "error": "AI service temporarily unavailable. Contact IT support."}), 500
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    prompt = f"""You are MediBot, an AI Healthcare Assistant.

Rules:
- Answer ONLY healthcare, medical, wellness, and nutrition questions.
- Format answers using bullet points (•) and bold titles for readability.
- Keep answers concise: 4–6 bullet points max.
- If the question is completely unrelated to healthcare, politely redirect.
- Always end with: "⚠️ Consult a licensed healthcare professional for personal medical advice."

User question: {message}"""
    
    try:
        import urllib.request
        req_data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=8) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            reply = resp_data["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"success": True, "reply": reply})
    except Exception as e:
        print(f"Chatbot API error: {e}")
        return jsonify({"success": False, "error": "API query timeout or quota limit reached."}), 500


# ─────────────────────────────────────────────
#  PRESCRIPTION OCR
# ─────────────────────────────────────────────
@app.route("/ocr")
def ocr():
    return render_template("ocr.html", user=get_current_user())


# ─────────────────────────────────────────────
#  ANALYTICS
# ─────────────────────────────────────────────
@app.route("/analytics")
def analytics():
    user  = get_current_user()
    conn  = get_db()
    stats = conn.execute("SELECT * FROM health_stats ORDER BY stat_date ASC").fetchall()
    conn.close()
    return render_template("analytics.html", user=user, stats=stats)


@app.route("/analytics/predict", methods=["POST"])
def predict_risk():
    data    = request.json or {}
    age     = int(data.get("age", 30))
    bp      = int(data.get("bp", 120))
    glucose = int(data.get("glucose", 100))
    bmi     = float(data.get("bmi", 22))

    score = 0
    if age > 60: score += 25
    elif age > 45: score += 15
    if bp > 140: score += 35
    elif bp > 130: score += 20
    if glucose > 126: score += 35
    elif glucose > 100: score += 20
    if bmi > 30: score += 20
    elif bmi > 25: score += 10

    score = min(score, 100)
    if score >= 70:
        level, color, advice = "High Risk", "danger", "Immediate medical consultation recommended."
    elif score >= 40:
        level, color, advice = "Moderate Risk", "warning", "Schedule a routine check-up soon."
    else:
        level, color, advice = "Low Risk", "success", "Keep maintaining your healthy lifestyle!"

    return jsonify({"success": True, "risk_score": score, "level": level, "color": color, "advice": advice})


# ─────────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────────
@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = get_current_user()
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        conn     = get_db()
        if password:
            conn.execute("UPDATE users SET name=?,email=?,password=? WHERE id=?",
                         (name, email, generate_password_hash(password), user["id"]))
        else:
            conn.execute("UPDATE users SET name=?,email=? WHERE id=?", (name, email, user["id"]))
        conn.commit()
        conn.close()
        session["user_name"]  = name
        session["user_email"] = email
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html", user=user)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
