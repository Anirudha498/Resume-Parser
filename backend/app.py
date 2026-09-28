from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2

from parser import parse_resume


app = Flask(__name__)
CORS(app)


# ==============================
# PostgreSQL Connection
# ==============================

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="resume_parser",
        user="postgres",
        password="Your-Password",
        port="5432"
    )


# ==============================
# Upload Resume
# ==============================

@app.route("/upload", methods=["POST"])
def upload_resume():

    try:

        # Check resume file
        if "resume" not in request.files:
            return jsonify({
                "error": "No resume file uploaded"
            }), 400

        file = request.files["resume"]

        if file.filename == "":
            return jsonify({
                "error": "No file selected"
            }), 400


        # ==============================
        # File Validation
        # ==============================

        allowed_extensions = [".pdf", ".docx"]

        extension = os.path.splitext(
            file.filename
        )[1].lower()

        if extension not in allowed_extensions:
            return jsonify({
                "error": "Only PDF and DOCX files are allowed"
            }), 400


        # Maximum file size = 2 MB

        file.seek(0, os.SEEK_END)

        file_size = file.tell()

        file.seek(0)

        if file_size > 2 * 1024 * 1024:
            return jsonify({
                "error": "File size should be less than 2MB"
            }), 400


        # ==============================
        # Save Uploaded File
        # ==============================

        upload_folder = "uploads"

        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(
            upload_folder,
            file.filename
        )

        file.save(file_path)


        # ==============================
        # Get Job Description
        # ==============================

        job_desc = request.form.get(
            "job_desc",
            ""
        )


        # ==============================
        # Parse Resume
        # ==============================

        data = parse_resume(
            file_path,
            job_desc
        )


        # ==============================
        # PostgreSQL Insert
        # ==============================

        conn = get_db_connection()

        cursor = conn.cursor()


        cursor.execute(
            """
            INSERT INTO resume
            (
                name,
                email,
                phone,
                skills,
                education,
                experience,
                projects,
                match_score,
                job_skills,
                skill_gap
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,

            (
                data.get("name"),

                data.get("email"),

                data.get("phone"),

                ", ".join(
                    data.get("skills", [])
                ),

                data.get("education"),

                data.get("experience"),

                data.get("projects"),

                float(data.get("match_score",0)),

                ", ".join(
                    data.get("job_skills", [])
                ),

                ", ".join(
                    data.get("skill_gap", [])
                )
            )
        )


        conn.commit()

        cursor.close()

        conn.close()


        # ==============================
        # Send Result to React
        # ==============================

        return jsonify(data), 200


    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# ==============================
# Run Flask
# ==============================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )