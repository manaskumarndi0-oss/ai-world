from flask import Flask, render_template, request, redirect
import os
import sqlite3

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database create
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL
)
""")

conn.commit()
conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("image")

    if file and file.filename:

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO images(filename) VALUES(?)",
            (file.filename,)
        )

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

    images = []

    for row in rows:
        images.append("/static/uploads/" + row[0])

    return render_template("gallery.html", images=images)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
