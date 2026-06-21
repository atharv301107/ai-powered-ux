from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
from datetime import date

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB_PATH = Path("healthcare_admin.db")


# ---------------- Database Helper ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active',
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        doctor_name TEXT NOT NULL,
        appointment_date TEXT NOT NULL,
        department TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stat_date TEXT NOT NULL,
        patients_count INTEGER NOT NULL,
        doctors_count INTEGER NOT NULL,
        appointments_count INTEGER NOT NULL,
        emergency_cases INTEGER NOT NULL
    )
    """)

    # Default admin
    admin = cur.execute("SELECT id FROM users WHERE email=?", ("admin@gmail.com",)).fetchone()
    if not admin:
        cur.execute(
            "INSERT INTO users(name,email,password,role,status,created_at) VALUES(?,?,?,?,?,?)",
            (
                "Admin User",
                "admin@gmail.com",
                generate_password_hash("admin123"),
                "Admin",
                "Active",
                str(date.today()),
            ),
        )

    # Sample data only first time
    count_users = cur.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
    if count_users == 1:
        sample_users = [
            ("Dr. Sneha Patil", "doctor@gmail.com", generate_password_hash("doctor123"), "Doctor", "Active", str(date.today())),
            ("Rahul Sharma", "patient@gmail.com", generate_password_hash("patient123"), "Patient", "Active", str(date.today())),
            ("Reception Staff", "staff@gmail.com", generate_password_hash("staff123"), "Staff", "Active", str(date.today())),
        ]
        cur.executemany(
            "INSERT INTO users(name,email,password,role,status,created_at) VALUES(?,?,?,?,?,?)",
            sample_users,
        )

    count_appt = cur.execute("SELECT COUNT(*) AS total FROM appointments").fetchone()["total"]
    if count_appt == 0:
        sample_appts = [
            ("Amit Kadam", "Dr. Sneha Patil", "2026-06-16", "Cardiology", "Confirmed"),
            ("Priya Jadhav", "Dr. Mehta", "2026-06-17", "Dental", "Pending"),
            ("Rohit Mali", "Dr. Khan", "2026-06-18", "Orthopedic", "Completed"),
            ("Neha Pawar", "Dr. Patil", "2026-06-19", "General", "Cancelled"),
        ]
        cur.executemany(
            "INSERT INTO appointments(patient_name,doctor_name,appointment_date,department,status) VALUES(?,?,?,?,?)",
            sample_appts,
        )

    count_stats = cur.execute("SELECT COUNT(*) AS total FROM health_stats").fetchone()["total"]
    if count_stats == 0:
        sample_stats = [
            ("2026-06-11", 120, 15, 38, 4),
            ("2026-06-12", 145, 16, 45, 6),
            ("2026-06-13", 160, 16, 52, 8),
            ("2026-06-14", 132, 17, 41, 5),
            ("2026-06-15", 175, 17, 59, 9),
        ]
        cur.executemany(
            "INSERT INTO health_stats(stat_date,patients_count,doctors_count,appointments_count,emergency_cases) VALUES(?,?,?,?,?)",
            sample_stats,
        )

    conn.commit()
    conn.close()


@app.before_request
def require_login():
    allowed_routes = ["login", "static"]
    if request.endpoint not in allowed_routes and "admin_id" not in session:
        return redirect(url_for("login"))


# ---------------- Auth ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND role='Admin'", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["admin_id"] = user["id"]
            session["admin_name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Invalid admin email or password", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- Dashboard ----------------
@app.route("/")
def dashboard():
    conn = get_db()
    total_users = conn.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
    total_doctors = conn.execute("SELECT COUNT(*) AS total FROM users WHERE role='Doctor'").fetchone()["total"]
    total_patients = conn.execute("SELECT COUNT(*) AS total FROM users WHERE role='Patient'").fetchone()["total"]
    total_appointments = conn.execute("SELECT COUNT(*) AS total FROM appointments").fetchone()["total"]
    pending_appointments = conn.execute("SELECT COUNT(*) AS total FROM appointments WHERE status='Pending'").fetchone()["total"]

    role_rows = conn.execute("SELECT role, COUNT(*) AS total FROM users GROUP BY role").fetchall()
    appointment_rows = conn.execute("SELECT status, COUNT(*) AS total FROM appointments GROUP BY status").fetchall()
    recent_appointments = conn.execute("SELECT * FROM appointments ORDER BY appointment_date DESC LIMIT 5").fetchall()
    latest_stats = conn.execute("SELECT * FROM health_stats ORDER BY stat_date DESC LIMIT 7").fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_doctors=total_doctors,
        total_patients=total_patients,
        total_appointments=total_appointments,
        pending_appointments=pending_appointments,
        role_labels=[r["role"] for r in role_rows],
        role_data=[r["total"] for r in role_rows],
        appointment_labels=[r["status"] for r in appointment_rows],
        appointment_data=[r["total"] for r in appointment_rows],
        recent_appointments=recent_appointments,
        stat_dates=[r["stat_date"] for r in reversed(latest_stats)],
        patient_counts=[r["patients_count"] for r in reversed(latest_stats)],
        emergency_counts=[r["emergency_cases"] for r in reversed(latest_stats)],
    )


# ---------------- User Management ----------------
@app.route("/users")
def users():
    search = request.args.get("search", "")
    role = request.args.get("role", "")

    query = "SELECT * FROM users WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR email LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if role:
        query += " AND role=?"
        params.append(role)

    query += " ORDER BY id DESC"

    conn = get_db()
    user_list = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("users.html", users=user_list, search=search, role=role)


@app.route("/users/add", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        status = request.form["status"]

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users(name,email,password,role,status,created_at) VALUES(?,?,?,?,?,?)",
                (name, email, generate_password_hash(password), role, status, str(date.today())),
            )
            conn.commit()
            conn.close()
            flash("User added successfully", "success")
            return redirect(url_for("users"))
        except sqlite3.IntegrityError:
            flash("Email already exists", "danger")

    return render_template("user_form.html", title="Add User", user=None)


@app.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        role = request.form["role"]
        status = request.form["status"]
        password = request.form.get("password", "")

        if password:
            conn.execute(
                "UPDATE users SET name=?, email=?, password=?, role=?, status=? WHERE id=?",
                (name, email, generate_password_hash(password), role, status, user_id),
            )
        else:
            conn.execute(
                "UPDATE users SET name=?, email=?, role=?, status=? WHERE id=?",
                (name, email, role, status, user_id),
            )
        conn.commit()
        conn.close()
        flash("User updated successfully", "success")
        return redirect(url_for("users"))

    conn.close()
    return render_template("user_form.html", title="Edit User", user=user)


@app.route("/users/delete/<int:user_id>")
def delete_user(user_id):
    if session.get("admin_id") == user_id:
        flash("You cannot delete your own admin account", "warning")
        return redirect(url_for("users"))

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    flash("User deleted successfully", "success")
    return redirect(url_for("users"))


# ---------------- Appointment Reports ----------------
@app.route("/appointments")
def appointments():
    status = request.args.get("status", "")
    query = "SELECT * FROM appointments WHERE 1=1"
    params = []
    if status:
        query += " AND status=?"
        params.append(status)
    query += " ORDER BY appointment_date DESC"

    conn = get_db()
    appointment_list = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("appointments.html", appointments=appointment_list, status=status)


@app.route("/appointments/add", methods=["GET", "POST"])
def add_appointment():
    if request.method == "POST":
        conn = get_db()
        conn.execute(
            "INSERT INTO appointments(patient_name,doctor_name,appointment_date,department,status) VALUES(?,?,?,?,?)",
            (
                request.form["patient_name"],
                request.form["doctor_name"],
                request.form["appointment_date"],
                request.form["department"],
                request.form["status"],
            ),
        )
        conn.commit()
        conn.close()
        flash("Appointment added successfully", "success")
        return redirect(url_for("appointments"))

    return render_template("appointment_form.html", title="Add Appointment", appointment=None)


@app.route("/appointments/edit/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    conn = get_db()
    appointment = conn.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()

    if request.method == "POST":
        conn.execute(
            "UPDATE appointments SET patient_name=?, doctor_name=?, appointment_date=?, department=?, status=? WHERE id=?",
            (
                request.form["patient_name"],
                request.form["doctor_name"],
                request.form["appointment_date"],
                request.form["department"],
                request.form["status"],
                appointment_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Appointment updated successfully", "success")
        return redirect(url_for("appointments"))

    conn.close()
    return render_template("appointment_form.html", title="Edit Appointment", appointment=appointment)


@app.route("/appointments/delete/<int:appointment_id>")
def delete_appointment(appointment_id):
    conn = get_db()
    conn.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
    conn.commit()
    conn.close()
    flash("Appointment deleted successfully", "success")
    return redirect(url_for("appointments"))


# ---------------- Healthcare Statistics ----------------
@app.route("/health-stats", methods=["GET", "POST"])
def health_stats():
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO health_stats(stat_date,patients_count,doctors_count,appointments_count,emergency_cases) VALUES(?,?,?,?,?)",
            (
                request.form["stat_date"],
                request.form["patients_count"],
                request.form["doctors_count"],
                request.form["appointments_count"],
                request.form["emergency_cases"],
            ),
        )
        conn.commit()
        flash("Healthcare statistics saved", "success")
        return redirect(url_for("health_stats"))

    stats = conn.execute("SELECT * FROM health_stats ORDER BY stat_date DESC").fetchall()
    conn.close()
    return render_template("health_stats.html", stats=stats)


@app.route("/health-stats/delete/<int:stat_id>")
def delete_health_stat(stat_id):
    conn = get_db()
    conn.execute("DELETE FROM health_stats WHERE id=?", (stat_id,))
    conn.commit()
    conn.close()
    flash("Health statistic deleted", "success")
    return redirect(url_for("health_stats"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
