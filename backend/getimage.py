from flask import Flask, request, g, current_app, session, send_file, render_template, jsonify
from flask_cors import CORS, cross_origin
import numpy as np 
import pandas as pd
import flask
import json
from filelock import FileLock, Timeout

app = Flask(__name__)
CORS(app)

users_db = {}
app.secret_key = "supersecretkey"  # Required for session management


@app.route('/setconfig', methods=['POST'])
@cross_origin()
def setconfig():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        lock = FileLock("config.json.lock", thread_local=False)
        with lock:
            with open("config.json", "w") as config:
                json.dump(data, config, indent=2)
        response = {"message": "Received"}
        return jsonify(response), 201
'''
@app.route('/', methods=['GET'])
@cross_origin()
def index():
    images = pd.read_csv("images.csv")
    print(images)
    camera = 'camera.png'
    detections = ['detection.png']
    return render_template('index.html', cam = camera, detections = detections)
'''
@app.route('/geturls', methods=['GET'])
@cross_origin()
def getimgurls():

    months = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December"
    }

    images = pd.read_csv("images.csv")
    imgs = images.values.tolist()
    urls = []
    for img in imgs:
        obj = {}
        #urls.append(img[0])
        data = img[0].split("-")
        obj["animal"] = data[0][7:]

        hour = int(data[4])
        half = "AM"

        if hour >= 12 and hour <= 23:
            half = "PM"

        hour = hour % 12

        if hour == 0:
            hour = 12

        timeInfo = str(hour) + ":" + data[5] + " " + half
        date = months[data[2]] + " " + data[3] + ", " + data[1]
        obj["date"] = date
        obj["timeInfo"] = timeInfo

        obj["url"] = img[0]

        urls.append(obj)

    response = {"urls": urls}
    return jsonify(response), 201

# Signup API (NO Password Hashing)
@app.route("/api/signup", methods=["POST"])
def signup():
    """Handles user signup (PLAIN TEXT passwords, for testing only)"""
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Invalid data"}), 400

    username = data["username"].strip()
    password = data["password"].strip()

    if not username or not password:
        return jsonify({"error": "Username and password cannot be empty"}), 400

    if username in users_db:
        return jsonify({"error": "User already exists"}), 400

    # Store password as plain text (for testing only)
    users_db[username] = password

    print(f"User '{username}' registered successfully.")  # Debugging output
    return jsonify({"message": "Signup successful"}), 200

# Login API (PLAIN TEXT Passwords)
@app.route("/api/login", methods=["POST"])
def login():
    """Handles user login (NO password hashing)"""
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if username not in users_db or users_db[username] != password:
        print(f"Login failed for '{username}'. Incorrect username or password.")  # Debugging output
        return jsonify({"error": "Invalid username or password"}), 401

    # Login successful Set session
    session["username"] = username
    print(f"Login successful for '{username}'.")  # Debugging output
    print("Login successful, session =", dict(session)) # Debugging output
    return jsonify({"message": "Login successful"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)