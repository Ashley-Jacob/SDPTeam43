from flask import Flask, request, abort, jsonify
import requests
#from picamera2 import Picamera2
import cv2
import time
import os
import threading

inst = Flask(__name__)
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print('Could not open webcam')
    exit()
#cam = Picamera2()
#config = cam.create_preview_configuration(main={"size": (1920, 1080)}, sensor={"output_size": (2592,1944)})
#cam.configure(config)
#cam.start()
time.sleep(1)

webserver = '10.194.215.27'

imagefolder = './images' # directory for the images
if not os.path.exists(imagefolder):
    os.makedirs(imagefolder)\

signalfolder = './signals' # directory for the images
if not os.path.exists(signalfolder):
    os.makedirs(signalfolder)

stop_event = threading.Event()  # stop event to signal threads to exit (fix Keyboard Interrupt issue)

def run():
    #ssl_context = (r'C:\Users\dalyt\Documents\SDP\server.crt', r'C:\Users\dalyt\Documents\SDP\private.key') # (certificate, private key)
    inst.run(host='10.194.215.27', port=5001, use_reloader=False)#, ssl_context=ssl_context, debug=True) # port 5000 used for development

def background():
    while not stop_event.is_set():
        send_picture()
        time.sleep(2)

#thread = threading.Thread(target=run)
#thread.start()
#background_thread = threading.Thread(target=background, daemon=True)
#background_thread.start()

def send_file_to_server(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        try:
            response = requests.post('http://' + webserver + ':5000/upload', files=files)
            print(response)
            return response
        except Exception as e:
            print(e)
            return e
    #return response

def send_picture():
    timestamp = time.strftime('%m-%d-%Y_%H-%M-%S')
    file_path = os.path.join(imagefolder, f'image_{timestamp}.jpg')
    ret, frame = cam.read()
    if ret:
        cv2.imwrite(file_path, frame)
    #image_array = cv2.imread(file_path)
    send_file_to_server(file_path)
    try:
        os.remove(file_path)
    except OSError as e:
        print(f'{file_path} not found')
    #time.sleep(2)

@inst.before_request # IP filter (makeshift firewall)
def limit_remote_addr():
    if request.remote_addr != webserver:
        abort(403) # "Forbidden" HTTP status code

@inst.route('/')
def index():
    return

@inst.route('/upload', methods=['POST']) # only allow POST method (for uploading)
def upload(): # recieve "bear" or "no bear" message
    #if 'file' not in request.files:
    #    return 'No file in the request', 400 # "Bad request" HTTP status code
    #file = request.files['file']
    #print(file)
    #timestamp = time.strftime('%m-%d-%Y_%H-%M-%S')
    #file_path = fr'C:\Users\dalyt\Documents\SDP\signals\signal_{timestamp}.txt'
    #file.save(file_path) # save the file
    try:
        '''with open (file_path, 'r') as f:
            f.seek(0)
            print(f.read())
            f.seek(0)
            if f.read() == 'bear':
                print('BEAR!!!')
            else:
                print('no bear')'''
        data = request.get_json()
        signal = data['signal']
        #print(signal)
        if signal == "bear":
            print('BEAR!!!')
        else:
            print('no bear')
        #return jsonify({'message': 'Signal Delivered', 'file_path':file_path}), 200
        return jsonify({'message': 'Signal Delivered', 'signal':signal}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Error', 'exception': str(e)}), 500

if __name__ == '__main__':
    #ssl_context = (r'', r'') # (certificate, private key)
    #inst.run(host='10.194.215.27', port=5001)#, ssl_context=ssl_context, debug=True) # port 5000 used for development
    #while True:
        #send_picture()
    
    try:
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        background_thread = threading.Thread(target=background, daemon=True)
        background_thread.start()

        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print('--Keyboard Interrupt--')
        stop_event.set()
        time.sleep(2)