from flask import Flask, request, g, current_app, session, send_file, render_template, jsonify
from flask_cors import CORS, cross_origin
import numpy as np 
import pandas as pd
import flask
import json
from filelock import FileLock, Timeout

app = Flask(__name__)
CORS(app)

@app.route('/getimages', methods=['GET'])
@cross_origin()
def getimages():
    path = 'C:/Users/rubas/OneDrive/Documents/Random/beartest1.jpg'
    return send_file(path)

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

@app.route('/', methods=['GET'])
@cross_origin()
def index():
    images = pd.read_csv("images.csv")
    print(images)
    camera = 'camera.png'
    detections = ['detection.png']
    return render_template('index.html', cam = camera, detections = detections)

@app.route('/geturls', methods=['GET'])
@cross_origin()
def getimgurls():
    images = pd.read_csv("images.csv")
    imgs = images.values.tolist()
    urls = []
    for img in imgs:
        urls.append(img[0])

    response = {"urls": urls}
    return jsonify(response), 201

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)