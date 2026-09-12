from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import math

app = Flask(__name__)
app.secret_key = "blood_donor_secret_key_2026"

DATABASE = "database.db"


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT,
            blood_group TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            pincode TEXT,
            latitude REAL,
            longitude REAL,
            available TEXT DEFAULT 'Yes',
            last_donation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# HOME / LOGIN
# =========================================================

@app.route("/")
def index():
    if "mobile" in session:
        return redirect(url_for("home"))

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        mobile = request.form.get("mobile", "").strip()

        if not mobile:
            flash("Please enter your mobile number.", "danger")
            return redirect(url_for("login"))

        if not mobile.isdigit():
            flash("Please enter numbers only.", "danger")
            return redirect(url_for("login"))

        if len(mobile) < 10:
            flash("Please enter a valid mobile number.", "danger")
            return redirect(url_for("login"))

        session["mobile"] = mobile

        conn = get_db()
        donor = conn.execute(
            "SELECT * FROM donors WHERE mobile = ?",
            (mobile,)
        ).fetchone()
        conn.close()

        if donor:
            return redirect(url_for("home"))

        return redirect(url_for("register"))

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =========================================================
# HOME
# =========================================================

@app.route("/home")
def home():

    if "mobile" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    donor_count = conn.execute(
        "SELECT COUNT(*) FROM donors"
    ).fetchone()[0]

    blood_groups = conn.execute("""
        SELECT blood_group, COUNT(*) AS count
        FROM donors
        GROUP BY blood_group
    """).fetchall()

    donor = conn.execute(
        "SELECT * FROM donors WHERE mobile = ?",
        (session["mobile"],)
    ).fetchone()

    conn.close()

    return render_template(
        "home.html",
        donor_count=donor_count,
        blood_groups=blood_groups,
        donor=donor
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "mobile" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    donor = conn.execute(
        "SELECT * FROM donors WHERE mobile = ?",
        (session["mobile"],)
    ).fetchone()

    conn.close()

    if donor is None:
        return redirect(url_for("register"))

    return render_template("profile.html", donor=donor)


# =========================================================
# DONOR REGISTRATION
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if "mobile" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        mobile = session["mobile"]

        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        blood_group = request.form.get("blood_group", "").strip()
        contact = request.form.get("contact", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        latitude = request.form.get("latitude", "").strip()
        longitude = request.form.get("longitude", "").strip()
        available = request.form.get("available", "Yes")
        last_donation = request.form.get("last_donation", "").strip()

        # Required field validation
        if not name or not age or not blood_group or not contact:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("register"))

        if not address or not city or not state:
            flash("Please enter complete address details.", "danger")
            return redirect(url_for("register"))

        try:
            age = int(age)
        except ValueError:
            flash("Age must be a number.", "danger")
            return redirect(url_for("register"))

        if age < 18 or age > 65:
            flash("Please enter an age between 18 and 65.", "danger")
            return redirect(url_for("register"))

        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            latitude = None
            longitude = None

        conn = get_db()

        existing = conn.execute(
            "SELECT id FROM donors WHERE mobile = ?",
            (mobile,)
        ).fetchone()

        if existing:

            conn.execute("""
                UPDATE donors SET
                    name = ?,
                    age = ?,
                    gender = ?,
                    blood_group = ?,
                    contact = ?,
                    email = ?,
                    address = ?,
                    city = ?,
                    state = ?,
                    pincode = ?,
                    latitude = ?,
                    longitude = ?,
                    available = ?,
                    last_donation = ?
                WHERE mobile = ?
            """, (
                name,
                age,
                gender,
                blood_group,
                contact,
                email,
                address,
                city,
                state,
                pincode,
                latitude,
                longitude,
                available,
                last_donation,
                mobile
            ))

        else:

            conn.execute("""
                INSERT INTO donors (
                    mobile,
                    name,
                    age,
                    gender,
                    blood_group,
                    contact,
                    email,
                    address,
                    city,
                    state,
                    pincode,
                    latitude,
                    longitude,
                    available,
                    last_donation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mobile,
                name,
                age,
                gender,
                blood_group,
                contact,
                email,
                address,
                city,
                state,
                pincode,
                latitude,
                longitude,
                available,
                last_donation
            ))

        conn.commit()
        conn.close()

        flash("Donor profile saved successfully!", "success")

        return redirect(url_for("profile"))

    return render_template("register.html")


# =========================================================
# SEARCH DONORS
# =========================================================

@app.route("/search", methods=["GET", "POST"])
def search():

    if "mobile" not in session:
        return redirect(url_for("login"))

    donors = []
    selected_group = ""
    selected_city = ""

    if request.method == "POST":

        selected_group = request.form.get("blood_group", "").strip()
        selected_city = request.form.get("city", "").strip()

        conn = get_db()

        query = """
            SELECT * FROM donors
            WHERE blood_group = ?
            AND available = 'Yes'
        """

        params = [selected_group]

        if selected_city:
            query += " AND LOWER(city) LIKE LOWER(?)"
            params.append("%" + selected_city + "%")

        query += " ORDER BY name"

        donors = conn.execute(query, params).fetchall()

        conn.close()

    return render_template(
        "search.html",
        donors=donors,
        selected_group=selected_group,
        selected_city=selected_city
    )


# =========================================================
# ALL DONORS
# =========================================================

@app.route("/donors")
def donors():

    if "mobile" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    all_donors = conn.execute("""
        SELECT * FROM donors
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    return render_template(
        "donors.html",
        donors=all_donors
    )


# =========================================================
# DONOR MAP DATA
# =========================================================

@app.route("/map")
def donor_map():

    if "mobile" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    donors = conn.execute("""
        SELECT id, name, blood_group, contact,
               address, city, state,
               latitude, longitude
        FROM donors
        WHERE latitude IS NOT NULL
        AND longitude IS NOT NULL
        AND available = 'Yes'
    """).fetchall()

    conn.close()

    return render_template(
        "search.html",
        donors=donors,
        selected_group="",
        selected_city=""
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    print("----------------------------------------")
    print(" BLOOD DONOR SEARCH SYSTEM")
    print("----------------------------------------")
    print("Server running at:")
    print("http://127.0.0.1:5000")
    print("----------------------------------------")

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )