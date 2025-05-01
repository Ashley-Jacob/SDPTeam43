from ultralytics import YOLO
import pygame
import cv2
import os
import random
import datetime
import threading
import time
import json
import pandas as pd
from filelock import Timeout, FileLock

class Detector:

    def __init__(self):
        self.isDetected = False
        self.event = threading.Event()
        self.event.clear()
        self.mutex = threading.Lock()
        self.cond = threading.Condition()
        self.trigger_time = datetime.datetime.now()
        self.alarm_length = 10

    def get_detected(self):
        return self.isDetected

    def set_detected(self, val):
        self.isDetected = val
        if self.isDetected:
            self.trigger_time = datetime.datetime.now()

    def set_alarm_length(self, val):
        self.alarm_length = val

    def check_reset(self):
        interval = (datetime.datetime.now() - self.trigger_time).total_seconds()
        if interval > self.alarm_length:
            self.isDetected = False


def sound(detector):
    pygame.init()

    airhorn = pygame.mixer.Sound('C:/Users/rubas/OneDrive/Documents/Random/airhorn.mp3')
    potsnpans = pygame.mixer.Sound('C:/Users/rubas/OneDrive/Documents/Random/potsnpans.mp3')
    laser = pygame.mixer.Sound('C:/Users/rubas/OneDrive/Documents/Random/laser.mp3')
    glass = pygame.mixer.Sound('C:/Users/rubas/OneDrive/Documents/Random/glass.wav')
    whistle = pygame.mixer.Sound('C:/Users/rubas/OneDrive/Documents/Random/whistle.wav')

    sound_options = {
        "airhorn": airhorn,
        "potsnpans": potsnpans,
        "laser": laser,
        "glass": glass,
        "whistle": whistle
    }

    sounds = []

    lock = FileLock("config.json.lock", thread_local=False)

    while True:
        with detector.cond:
            while not detector.get_detected():
                detector.cond.wait()
            detector.check_reset()

        try:
            data = dict()
            with lock:
                with open("config.json", "r") as config:
                    data = json.load(config)
            sounds = []
            for sound in data["sounds"]:
                sounds.append(sound_options[sound])
            detector.set_alarm_length(data["alarmLen"])
        except:
            print("Sound configuration error")

        if len(sounds) == 0:
            sounds = [airhorn]
            
        noise = random.choice(sounds)
        noise.play()
        time.sleep(.5)

def detection(detector):
    model = YOLO('yolov8n.pt')

    animals = []
    trig_alarm = []
    gen_interval = 30
    det_interval = 60
    image_limit = 10

    lock = FileLock("config.json.lock", thread_local=False)

    classes = {
        "tensor([15.])": "Cat",
        "tensor([16.])": "Dog",
        "tensor([21.])": "Bear",
        "tensor([0.])": "Person"
    }

    last_detection = None
    time_between = 0
    time_since = 0
    last_image = datetime.datetime.now()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        try:
            data = dict()
            with lock:
                with open("config.json", "r") as config:
                    data = json.load(config)
            animals = data['detect']
            trig_alarm = data['triggerAlarm']
            gen_interval = data['genInterval']
            det_interval = data['detInterval']
            image_limit = data['imgLimit']
        except:
            print("Configuration Error")

        # frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        results = model(frame, verbose=False)

        now = datetime.datetime.now()

        time_since = (now - last_image).total_seconds()
        if time_since > gen_interval:
            last_image = now
            cv2.imwrite("static/camera.png", frame)

        annotated_frame = results[0].plot()

        # bear_class_id = 21
        detections = results[0].boxes
        for detection in detections:
            if detection.cls in animals:
                if last_detection == None:
                    time_between = det_interval + 1
                else:
                    time_between = (now - last_detection).total_seconds()

                if time_between > det_interval:
                    print(classes[str(detection.cls)] + " Detected: " + str(now))
                    last_detection = now
                    with open('detection.txt', 'a') as file:
                        file.write(classes[str(detection.cls)] + " Detected: " + str(now) +"\n") 
                    filename = "static/" + classes[str(detection.cls)]+ "-" + str(now).replace(" ", "-").replace(":","-") +".png"
                    imgs = pd.read_csv("images.csv")
                    imgs = pd.concat([imgs, pd.DataFrame([filename], columns=imgs.columns)], ignore_index=True)
                    if imgs.size > image_limit:
                        start = imgs.size - image_limit
                        imgs = imgs.iloc[start:]
                    imgs.to_csv("images.csv", index=False)
                    cv2.imwrite(filename, frame)
            if detection.cls in trig_alarm:
                with detector.cond:
                    detector.set_detected(True)
                    detector.cond.notify()
                break    
                
        cv2.imshow("Camera", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    arg = Detector()

    t1 = threading.Thread(target=sound, args=[arg,])
    t2 = threading.Thread(target=detection, args=[arg,])

    t1.start()
    t2.start()

    t1.join()
    t2.join()

