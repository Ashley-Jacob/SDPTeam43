from flask import Flask, request, abort, render_template, redirect, session, url_for, request, jsonify, send_from_directory, send_file, g, current_app
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, UserMixin
import requests
import os
import sys
import pymysql
from mysql.connector import Error
import time
import subprocess
import atexit
import logging
import threading
from ultralytics import YOLO
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import json
import socket
import numpy as np 
import pandas as pd
from filelock import FileLock, Timeout

inst = Flask(__name__, static_folder=r"static") # create flask instance
CORS(inst, supports_credentials=True, origins=["http://localhost:3000"]) # enable CORS for all routes
#login_manager = LoginManager()
#login_manager.init_app(inst)

'''class User(UserMixin):
    def __init__(self, id, username, password):
        self.username = username
        self.password = password'''
#might not use this^

uploadfolder = './uploads' # directory for uploaded files
inst.config['UPLOAD_FOLDER'] = './uploads' # directory for uploaded files
inst.config['MAX_CONTENT_LENGTH'] = 100000000  # limit file size to 100 MB
secret_key = os.urandom(256) # generate a random secret key for session management
inst.secret_key = secret_key
model = YOLO('yolov8n.pt')

if not os.path.exists(inst.config['UPLOAD_FOLDER']):
    os.makedirs(inst.config['UPLOAD_FOLDER'])

if not os.path.exists(r'C:\Users\dalyt\Documents\SDP\signal.txt'):
    with open('signal.txt', 'w') as f:
        f.write('')

#logging.basicConfig(level=logging.DEBUG)
ip = socket.gethostbyname(socket.gethostname()) #host ip
piserver = '10.66.97.109' # ip address of Raspberry Pi
PI_PORT = 9000 # port number of the Raspberry Pi server
whitelist = {ip, piserver,'0.0.0.0'} # allowed IP addresses
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
    #ssl_context = (r'C:\Users\dalyt\Documents\SDP\server.crt', r'C:\Users\dalyt\Documents\SDP\private.key')
    inst.run(host='0.0.0.0', port=5000, use_reloader=False)#, ssl_context=ssl_context, debug=True) # port 5000 used for development

def start_yolo(): # for running yolo file - not using anymore (yolo() instead)
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

# def create_connection():
#     try:
#         connection = mysql.connector.connect( # connect to the SQL server and use the SDPlogin database
#             host='localhost',
#             user='Team43',
#             password='bearsRcool',
#             database='SDPlogin',
#             port='3307' # default is 3306, I'm using 3307 for this MySQL server because of conflicts
#         )
#         if connection.is_connected():
#             print('Connection Successful')
#             return connection
#     except Error as e:
#         print(f'Error: {e}')
#         return None
    
def create_connection():
    try:
        connection = pymysql.connect( # connect to the SQL server and use the SDPlogin database
            host='localhost',
            user='Team43',
            password='bearsRcool',
            database='SDPlogin',
            port=3307 # default is 3306, I'm using 3307 for this MySQL server because of conflicts
        )
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

#@inst.before_request # IP filter (makeshift firewall)
#def limit_remote_addr():
    #if request.remote_addr not in whitelist:
        #abort(403) # "Forbidden" HTTP status code

# @inst.route('/upload', methods=['POST']) # only allow POST method (for uploading)
# def upload():
#     #print('got to /upload', flush=True)
#     #inst.logger.debug("Debug message")
#     if request.method == 'POST':
#         if 'arr' not in request.json:
#             return 'No file in the request', 400 # "Bad request" HTTP status code
#         global arr 
#         arr = np.array(request.json['arr'])
#         print(arr.shape)
#         print(arr)
#         plt.imshow(arr)
#         plt.show()
#         #cv2.imshow('yolo', arr)
#         # exit when q is pressed
#         #cv2.waitKey(1) == ord('q')
#         print(type(arr))
#         #yolo(arr)
#         #print(f'Saving file to: {os.path.abspath(inst.config['UPLOAD_FOLDER'] + file.filename)}', flush=True)
#         #file.save(fr'C:\Users\dalyt\Documents\SDP\uploads\{file.filename}') # save the file
#     return 'File uploaded', 200 # "OK" HTTP status code

@inst.route('/api/signup', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
def signup():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Invalid data"}), 400 # "Bad request" HTTP status code
    username = data["username"].strip()
    password = data["password"].strip()
    if not username or not password:
        return jsonify({"error": "Username and password cannot be empty"}), 400
    success = False
    connection = create_connection()
    cursor = connection.cursor()
    try:
        query = "INSERT into userpass (Username, Password) VALUES (%s, %s);"
        cursor.execute(query, (username, password))
        connection.commit()
        success = True
        print(f'User "{username}" added successfully')
    except Error as e:
        if e.errno == 1062: # duplicate entry error code
            print(f"Error: '{e}'")
            return jsonify({"error": "User already exists"}), 400
        print(f"Error: '{e}'")
    finally:
        cursor.close()
        connection.close()
        if success:
            return jsonify({"message": "Signup successful"}), 200
        else:
            return jsonify({"error": "Error"}), 400

@inst.route('/api/login', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    connection = create_connection()
    cursor = connection.cursor()
    try:
        query = "SELECT Password FROM userpass WHERE Username = %s;"
        cursor.execute(query, (username,)) # parameterized query to prevent SQL injection
        queried_password = cursor.fetchone() # retrieves the next row of a query result set
        cursor.fetchall() # make sure there's no leftover rows in the query result set (prevent errors)
        if queried_password[0] == password:
            session['username'] = username
            print(f'User "{username}" logged in successfully')
            return jsonify({"message": "Login successful"}), 200 # "OK" HTTP status code
        else:
            print(f'User "{username}" failed to log in')
            return jsonify({"error": "Invalid username or password"}), 401 # "Unauthorized" HTTP status code
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        cursor.close()
        connection.close()

# Authentication Check API
@inst.route("/api/check-auth")
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
def check_auth():
    """Check if user is authenticated"""
    print("Current session contents:", dict(session)) # Dbugging output
    is_authenticated = "username" in session
    return jsonify({"authenticated": is_authenticated})

@inst.route('/api/logout')
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
def logout():
    session.pop('username', None)
    return jsonify({"message": "Logged out"}), 200

@inst.route('/setconfig', methods=['POST'])
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

@inst.route('/geturls', methods=['GET'])
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

# Serve React frontend
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

if __name__ == '__main__':
    #ssl_context = (r'C:\Users\dalyt\Documents\SDP\server.crt', r'C:\Users\dalyt\Documents\SDP\private.key')
    #inst.run(host='10.194.215.27', port=5000)#, ssl_context=ssl_context, debug=True) # port 5000 used for development
    #yolo = subprocess.run(["python", "yolo_for_server.py"])
    #atexit.register(yolo.terminate)
    #while True:
        #with open ('signal.txt', 'r+') as f:
            #if f.read() == 'bear':
                #send_file_to_server('signal.txt')
                #f.write('')
        #time.sleep(1)

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