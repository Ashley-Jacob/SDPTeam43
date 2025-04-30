from flask import Flask, request, jsonify, session, send_from_directory, abort, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
#from flask_mysqldb import MySQL
import os
from flask_cors import CORS  # Allow React frontend to communicate with Flask

import socket
import json

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests
import sys
import mysql.connector
from mysql.connector import Error
import time
import subprocess
import atexit
import logging
import threading
import msvcrt # for windows
#import fcntl # for linux
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt

#inst = Flask(__name__, static_folder="frontend/build", static_url_path="")
inst = Flask(__name__, static_folder="frontend/build", static_url_path=None)
inst.config['MAX_CONTENT_LENGTH'] = 100000000  # limit file size to 100 MB
secret_key = os.urandom(256) # generate a random secret key for session management
inst.secret_key = secret_key
model = YOLO('yolov8n.pt')

CORS(inst, supports_credentials=True)  # Allow CORS requests

# Temporary in-memory user database (storing passwords)
#users_db = {}
bcrypt = Bcrypt(inst)

login_manager = LoginManager()
login_manager.init_app(inst)
login_manager.login_view = "/login"  # Optional: where to redirect if not logged in
class User(UserMixin):
    def __init__(self, id, username):
        self.id = str(id)
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT ID, Username FROM USERPASS WHERE ID = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(id=row[0], username=row[1])
    except Error as e:
        print(f"User loader error: {e}")
    finally:
        cursor.close()
        connection.close()
    return None

'''
@login_manager.user_loader
def load_user(user_id):
    for username in users_db:
        if username == user_id:
            return User(id=username, username=username)
    return None
'''

if not os.path.exists(inst.config['UPLOAD_FOLDER']):
    os.makedirs(inst.config['UPLOAD_FOLDER'])

if not os.path.exists(r'C:\Users\dalyt\Documents\SDP\signal.txt'):
    with open('signal.txt', 'w') as f:
        f.write('')

#logging.basicConfig(level=logging.DEBUG)
ip = socket.gethostbyname(socket.gethostname()) #host ip
piserver = '10.66.97.109' # ip address of Raspberry Pi
whitelist = {ip, piserver} # allowed IP addresses
temp_db = {'Test':'Password'}
stop_event = threading.Event()  # stop event to signal threads to exit (fix Keyboard Interrupt issue)
arr = None

def send_file_to_server(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        try:
            response = requests.post('http://' + piserver + ':5001/upload', files=files)
            print(f'File sent to server: {response}')
            return response
        except Exception as e:
            print(e)
    #return response

def send_signal_to_server(signal):
    try:
        response = requests.post('http://' + piserver + ':5001/upload', json={'signal': signal})
        print(f'Signal <{signal}> sent to server: {response}')
        return response
    except Exception as e:
        print(e)

def run():
    ssl_context = (r'C:\Users\dalyt\Documents\SDP\server.crt', r'C:\Users\dalyt\Documents\SDP\private.key')
    inst.run(host=ip, port=5000, use_reloader=False, ssl_context=ssl_context, debug=True) # port 5000 used for development

def start_yolo():
    #yolo = subprocess.run(["python", "yolo_for_server.py"], capture_output=True)
    #yolo = subprocess.Popen(["python", "yolo_for_server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    yolo = subprocess.Popen(['python', 'yolo_for_server.py'], stdout=sys.stdout, stderr=sys.stderr, text=True)
    #atexit.register(yolo.terminate)

def yolo(arr):
    #atexit.register(cv2.destroyAllWindows())
    while not stop_event.is_set():
        while True:
            while True:
                timestamp = time.strftime('%m-%d-%Y_%H-%M-%S')
                init_time = time.time()
                print(timestamp)
                #file_path = os.path.join(fr'C:\Users\dalyt\Documents\SDP\uploads', f'image_{timestamp}.jpg')
                file_path = os.path.join(fr'C:\Users\dalyt\Documents\SDP\uploads', f'maybebear.jpg')
                time.sleep(1) #allow time for the file to be sent from pi
                try:
                    #image = Image.open(file_path)
                    #frame = np.array(image)
                    frame = arr
                    frame = frame[:,:,:3]
                    break
                except FileNotFoundError as e:
                    print(e)

            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()
            bear_class_id = 21
            detections = results[0].boxes
            for detection in detections:
                if detection.cls == bear_class_id:
                    end_time = time.time()
                    print(f'Runtime: {end_time - init_time}')
                    print("Bear Detected")
                    send_signal_to_server('bear')
                    break
                else: send_signal_to_server('no bear')
    

def background():
    while not stop_event.is_set():
        while True:
            with open (r'C:\Users\dalyt\Documents\SDP\signal.txt', 'r+') as f:
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, os.path.getsize(f.name)) # for windows
                    #fcntl.flock(f, fcntl.LOCK_EX) # for linux
                    if f.read() == 'bear':
                    #if True:
                        #send_file_to_server(r'C:\Users\dalyt\Documents\SDP\signal.txt')
                        send_signal_to_server('bear')
                        f.seek(0) # move file pointer to beginning of file
                        print(f'After Seek: {f.read()}')
                        f.truncate() # clear everything
                        print(f'After Truncate: {f.read()}')
                        f.write('')
                        print(f'After Write: {f.read()}')
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, os.path.getsize(f.name)) # for windows
                        #fcntl.flock(f, fcntl.LOCK_UN) # for linux
                    else: 
                        send_signal_to_server('no_bear')
                    break
                except PermissionError as e:
                    print(f'Webserver: {e}')
                    time.sleep(1)
        time.sleep(2)

#flask_thread = threading.Thread(target=run)
#flask_thread.start()
#yolo_thread = threading.Thread(target=start_yolo, daemon=True)
#yolo_thread.start()
#background_thread = threading.Thread(target=background, daemon=True)
#background_thread.start()

def create_connection():
    try:
        connection = mysql.connector.connect( # connect to the SQL server and use the SDPlogin database
            host='localhost',
            user='Team43',
            password='bearsRcool',
            database='SDPlogin',
            port='3307' # default is 3306, I'm using 3307 for this MySQL server because of conflicts
        )
        if connection.is_connected():
            print('Connection Successful')
            return connection
    except Error as e:
        print(f'Error: {e}')
        return None

def execute_query(connection, query): # executes a SQL query in the database
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print('Query Successful')
    except Error as e:
        print(f'Error: {e}')
    finally:
        cursor.close()
        connection.close

@inst.before_request # IP filter (makeshift firewall)
def limit_remote_addr():
    if request.remote_addr not in whitelist:
        abort(403) # "Forbidden" HTTP status code

# Signup API 
@inst.route("/api/signup", methods=["POST"])
def signup():
    """Handles user signup"""
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Invalid data"}), 400

    username = data["username"].strip()
    password = data["password"].strip()

    if not username or not password:
        return jsonify({"error": "Username and password cannot be empty"}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    connection = create_connection()
    cursor = connection.cursor()
    try:
        query = "INSERT into userpass (Username, Password) VALUES (%s, %s);"
        cursor.execute(query, (username, hashed_password))
        connection.commit()
        success = True
        print(f'User "{username}" added successfully')
        #temp_db[username] = password
        #print(temp_db)

    except mysql.connector.IntegrityError as e:
        #Need to specify username field as UNIQUE in mysql database
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Username already exists"}), 400
        return jsonify({"error": "Database error"}), 500
    
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        cursor.close()
        connection.close()
        if success: 
            return jsonify({"message": "Signup successful"}), 200

    '''if not username or not password:
        return jsonify({"error": "Username and password cannot be empty"}), 400

    if username in users_db:
        return jsonify({"error": "User already exists"}), 400

    # Hashed passwords with bcrypt
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users_db[username] = hashed_password

    print(f"User '{username}' registered successfully.")  # Debugging output
    return jsonify({"message": "Signup successful"}), 200
    '''

# Login API 
@inst.route("/api/login", methods=["POST"])
def login():
    """Handles user login"""
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password cannot be empty"}), 400
    
    #hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    connection = create_connection()
    cursor = connection.cursor()
    try:
        #query = "SELECT Password FROM userpass WHERE Username = %s;"
        query = "SELECT ID, Password FROM USERPASS WHERE Username = %s;" #get id and password
        cursor.execute(query, (username,)) # parameterized query to prevent SQL injection
        queried_password = cursor.fetchone() # retrieves the next row of a query result set (id, password)
        #print(username)
        #print(type(username))
        #print(queried_password)
        cursor.fetchall() # make sure there's no leftover rows in the query result set (prevent errors)
        #if temp_db[username]:
            #if temp_db[username] == password:
                #session['username'] = username
                #return redirect(url_for('dashboard', username=username))

        if queried_password:
            user_id = queried_password[0]
            hashed_password = queried_password[1]

        if bcrypt.check_password_hash(hashed_password, password):
            user = User(id=user_id, username=username)
            login_user(user)
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

        '''
        if queried_password[0] == hashed_password:
            # Use flask_login
            user = User(id=username, username=username)
            login_user(user)
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
        
            session['username'] = username
            return redirect(url_for('dashboard'))
        else: return redirect('/login')
        '''
    except Error as e:
        print(f"Error: '{e}'")
    #finally:
        cursor.close()
        connection.close()
    '''
    #if username not in users_db or users_db[username] != password:
    if username not in users_db:
        print(f"Login failed for '{username}'. Incorrect username or password.")  # Debugging output
        return jsonify({"error": "Invalid username or password"}), 401

    hashed_password = users_db[username]
        
    if not bcrypt.check_password_hash(hashed_password, password):
        print(f"Login failed for '{username}'. Incorrect username or password.")  # Debugging output
        return jsonify({"error": "Invalid username or password"}), 401

    # Login successful Set session
    #session["username"] = username
    
    # Use flask_login
    user = User(id=username, username=username)
    login_user(user)

    print(f"Login successful for '{username}'.")  # Debugging output
    return jsonify({"message": "Login successful"}), 200
    '''

# Logout API
@inst.route("/api/logout", methods=["POST"])
@login_required
def logout():
    """Ends user session"""
    #session.pop("username", None)
    logout_user() # flask_login logout
    print("User logged out successfully.") # Debugging output
    return jsonify({"message": "Logged out"}), 200

# Authentication Check API
@inst.route("/api/check-auth")
def check_auth():
    """Check if user is authenticated"""
    print("Current session contents:", dict(session)) # Dbugging output
    #is_authenticated = "username" in session
    is_authenticated = current_user.is_authenticated #flask_login library
    return jsonify({"authenticated": is_authenticated})

# Test Dashboard API (returns test image list)
@inst.route("/api/detections")
@login_required
def get_detections():
    """Fetch test detected images"""
    detections_folder = os.path.join("frontend", "public", "detections")

    # Ensure detections folder exists
    if not os.path.exists(detections_folder):
        os.makedirs(detections_folder)

    images = [img for img in os.listdir(detections_folder) if img.endswith(".jpg") or img.endswith(".png")]
    return jsonify({"message": "Welcome to the dashboard!", "detections": images})
    #return jsonify(images)

@inst.route("/api/dashboard")
@login_required
def dashboard():
    detections_path = os.path.join(os.path.dirname(__file__), "frontend", "public", "detections")
    return jsonify({"message": "Welcome to the dashboard!", "detections": os.listdir(detections_path)})

# Serve detection images
@inst.route("/detections/<path:filename>")
@login_required
def serve_detection_image(filename):
    return send_from_directory("frontend/public/detections", filename)

@inst.route("/static/<path:filename>")
def serve_static(filename):
        return send_from_directory(os.path.join(inst.static_folder, "static"), filename)
'''
@inst.route("/api/pi/config", methods=["GET"])
@login_required
def get_pi_config():
    return send_to_pi({"type": "get_config"})

@inst.route("/api/pi/config", methods=["POST"])
@login_required
def set_pi_config():
    data = request.get_json()
    return send_to_pi({"type": "set_config", "payload": data})
'''
@inst.route("/api/update-account", methods=["POST"])
@login_required
def update_account():
    data = request.get_json()
    new_username = data.get("new_username", "").strip()
    current_password = data.get("current_password", "").strip()
    new_password = data.get("new_password", "").strip()

    if not current_password:
        return jsonify({"error": "Current password required"}), 400

    connection = create_connection()
    cursor = connection.cursor()

    try:
        #Step 1: Get current user's username and password hash
        query = "SELECT Username, Password FROM USERPASS WHERE ID = %s;"
        cursor.execute(query, (current_user.id,))
        queried_data = cursor.fetchone()
        cursor.fetchall()
        if not queried_data:
            return jsonify({"error": "User not found"}), 404

        current_username, hashed_password = queried_data

        #Step 2: Verify password
        if not bcrypt.check_password_hash(hashed_password, current_password):
            return jsonify({"error": "Current password is incorrect"}), 401

        #Step 3: If changing username, check for duplicates
        if new_username and new_username != current_username:
            cursor.execute("SELECT ID FROM USERPASS WHERE Username = %s", (new_username,))
            if cursor.fetchone():
                return jsonify({"error": "Username already taken"}), 400
            cursor.execute("UPDATE USERPASS SET Username = %s WHERE ID = %s", (new_username, current_user.id))

        #Step 4: If changing password, hash and update
        if new_password:
            new_hashed = bcrypt.generate_password_hash(new_password).decode("utf-8")
            cursor.execute("UPDATE USERPASS SET Password = %s WHERE ID = %s", (new_hashed, current_user.id))

        connection.commit()

        #If username changed, refresh Flask-Login session
        if new_username and new_username != current_username:
            user = User(id=current_user.id, username=new_username)
            login_user(user)

        return jsonify({"message": "Account updated successfully"}), 200

    except Error as e:
        print(f"Update error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        cursor.close()
        connection.close()

#Serve React frontend
@inst.route("/", defaults={"path": ""})
@inst.route("/<path:path>")
def serve_react_app(path):
    """
    Serve React frontend for all routes except API endpoints.
    """
    # If the request is for an API endpoint, return a 404
    if path.startswith("api/"):
        return jsonify({"error": "API endpoint not found"}), 404

    # Serve the frontend React app
    return send_from_directory(inst.static_folder, "index.html")

# Run Flask Server
if __name__ == "__main__":
    #inst.run(host="0.0.0.0", port=5000, debug=True)
    try:
        flask_thread = threading.Thread(target=run, daemon=True)
        flask_thread.start()
        #yolo_thread = threading.Thread(target=start_yolo, daemon=True)
        #yolo_thread = threading.Thread(target=yolo, daemon=True)
        #yolo_thread.start()
        #background_thread = threading.Thread(target=background, daemon=True)
        #background_thread.start()

        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print('--Keyboard Interrupt--')
        stop_event.set()
        time.sleep(2)