from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import parse_resume
from supabase import create_client
import os

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://zdnxgmzipeijbcnsmmqu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkbnhnbXppcGVpamJjbnNtbXF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIyOTUxMDEsImV4cCI6MjA4Nzg3MTEwMX0.KiEn6VKzCSxocHk6_e4iGeLcF3bd83fzBv6AeYIKLH8"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

UPLOAD_FOLDER = "../resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    data = parse_resume(path)

    supabase.table("resume").insert(data).execute()

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)