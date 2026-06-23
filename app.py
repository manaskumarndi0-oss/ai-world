from flask import Flask, render_template, request, redirect, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "aiworld_2026_secure_key"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    file = request.files.get("image")

    if file and file.filename:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO images(filename) VALUES(?)", (file.filename,))

        conn.commit()
        conn.close()

    return redirect("/gallery")

@app.route("/gallery")
def gallery():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT filename FROM images ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    images = ["/static/uploads/" + row[0] for row in rows]

    return render_template("gallery.html", images=images)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user[0] == password:
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users(username, password) VALUES(?, ?)",
                       (username, password))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
