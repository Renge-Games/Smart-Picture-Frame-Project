#!/usr/bin/python3
# -*- coding: utf-8 -*-

from settings import *

import json
import os
from os import path
from typing import Dict

if RUNS_ON_RPI:
    import MPR121
import random
import sys
from threading import Thread, Event
import time
import tkinter

import cv2
from PIL import Image, ImageTk

import rotation
from VideoGet import VideoGet
from handtracking import hand_tracking
from rotation import Gyroscope
quitting = Event()


# ui thread declaration
class App(Thread):
    def __init__(self):
        self.initialized = False
        super().__init__()

    def callback(self):
        self.root.quit()

    def save_ratings(self):
        with open(path.join(IMAGE_PATH, imageRatingName), "w") as fp:
            json.dump(self.ratingsDict, fp)  # encode dict into JSON

    def update_files(self):
        self.names = os.listdir(IMAGE_PATH)
        if imageRatingName in self.names:
            self.names.remove(imageRatingName)
        print(self.names)
        self.historyIndex = 0  # the current index of the indexHistory list
        self.indexHistory = [0]  # the image history, each element represents the image index
        self.historyLimit = 100  # the maximum length of the history
        # load json
        self.ratingsDict: Dict[str, float] = {}
        try:
            with open(path.join(IMAGE_PATH, imageRatingName), "r") as fp:
                self.ratingsDict = json.load(fp)
        except Exception:
            pass
        finally:
            for name in self.names:
                if name not in self.ratingsDict.keys():
                    self.ratingsDict[name] = 1
        print(self.ratingsDict)

    def run(self):
        self.update_files()

        self.root = root = tkinter.Tk()
        self.w, self.h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.overrideredirect(1)
        root.geometry("%dx%d+0+0" % (self.w, self.h))
        root.focus_set()
        self.canvas = tkinter.Canvas(root, width=self.w, height=self.h)
        self.canvas.pack()
        self.canvas.configure(background='white')
        root.attributes("-fullscreen", True)

        pixelVirtual = tkinter.PhotoImage(width=1, height=1)
        # tkinter.Button(text="Prev", command=self.showPrevImg, image=pixelVirtual, width=50, height=self.h, compound="c").place(x=0,y=0)
        # tkinter.Button(text="Next", command=self.showNextImg, image=pixelVirtual, width=50, height=self.h, compound="c").place(x=self.w-75,y=0)
        tkinter.Button(text="Quit", command=self.quit, image=pixelVirtual, width=50, compound="c").place(x=self.w/2-25, y=0)
        self.faceText = tkinter.StringVar()
        tkinter.Label(self.root, textvariable=self.faceText).place(x=0, y=self.h-15)
        self.faceText.set("Image Score: -")
        self.show_image()
        self.initialized = True
        root.mainloop()

    def showPIL(self, pilImage):
        imgWidth, imgHeight = pilImage.size
        # resize photo to full screen
        ratio = min(self.w/imgWidth, self.h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth, imgHeight), Image.LANCZOS)
        self.root.image = image = ImageTk.PhotoImage(pilImage)  # prevent garbage collection
        imagesprite = self.canvas.create_image(self.w/2, self.h/2, image=image)

    def quit(self):
        print("Quitting App")
        self.root.destroy()
        quitting.set()
        self.root.quit()
        os._exit(1)  # exits all threads

    def get_img_index(self):
        return self.indexHistory[self.historyIndex]

    def get_current_img_rating(self):
        return self.get_img_rating(self.get_img_index())

    def get_img_rating(self, index):
        return self.ratingsDict.get(self.names[index])

    def get_random_weighted_image_index(self):
        current_index = self.get_img_index()  # all images except the current one
        file_names = list(self.ratingsDict.keys())
        weights = list(self.ratingsDict.values())
        if len(self.names) <= 1:  # nothing to compute if there is only one option
            return 0
        # select an image index that isn't currently already selected
        while True:
            randImg = random.choices(file_names, weights)
            if self.names.index(randImg[0]) != current_index:
                break

        return self.names.index(randImg[0])

    def show_image(self):
        file = Image.open(path.join(IMAGE_PATH, self.names[self.get_img_index()]))
        self.showPIL(file)

    def show_next_img(self):
        # new image index is always inserted at the start of the history
        # previous images are pushed off to higher indices in the history
        # historyIndex of 0 is considered the freshest image
        if self.historyIndex == 0:
            # insert
            self.indexHistory.insert(0, self.get_random_weighted_image_index())

            if len(self.indexHistory) > self.historyLimit:
                self.indexHistory.pop()
        else:
            # decrement
            self.historyIndex -= 1

        self.show_image()

    def show_prev_img(self):
        if len(self.indexHistory) <= self.historyIndex + 1:
            # we are at the tail end of our history, append a new image to the end to keep things seamless
            self.indexHistory.append(self.get_random_weighted_image_index())
            self.historyIndex += 1
            if len(self.indexHistory) > self.historyLimit:
                self.indexHistory.pop()
                self.historyIndex -= 1
        else:
            # increment
            self.historyIndex += 1
        self.show_image()

    def increase_img_rating(self):
        if self.ratingsDict.get(self.names[self.get_img_index()]) is None:
            self.ratingsDict[self.names[self.index]] = 1  # start at 1 to prevent divide by zero errors in the image selection
            print("New Image Detected!")
        if self.ratingsDict[self.names[self.get_img_index()]] < 5:  # limit
            self.ratingsDict[self.names[self.get_img_index()]] += 0.01
        self.save_ratings()


video_getter = VideoGet(0).start()
app = App()


def face_detection():
    # cv face-detection

    # Load the cascade
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    faceDetected = False
    startTime = time.time()
    autoImgChangeStartTime = time.time()
    try:
        while not quitting.is_set():
            # pi cap touch control
            if RUNS_ON_RPI and sensor.touch_status_changed():
                sensor.update_touch_data()
                for i in range(12):
                    if sensor.is_new_touch(i):
                        print("electrode {0} was just touched".format(i))
                        autoImgChangeStartTime = time.time()  # reset the slideshow timer
                        if i == 0:
                            app.show_next_img()
                        elif i == 1:
                            app.show_prev_img()

                    #elif sensor.is_new_release(i):
                    #    print ("electrode {0} was just released".format(i))

            # change the image automatically after a certain time
            if time.time() - autoImgChangeStartTime > autoImgChangeTime:
                app.show_next_img()
                autoImgChangeStartTime = time.time()  # reset the slideshow timer

            # opencv stuff and image rating

            # Read frame from webcam
            img = video_getter.frame
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Detect the faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            # update image score
            if len(faces) > 0:
                faceDetected = True
                print("ayo look, there's a face!")
            if time.time() - startTime > 1 and faceDetected:
                app.increase_img_rating()
                startTime = time.time()
                faceDetected = False

            # Display. This just changes the text of a label on the screen
            app.faceText.set("Image Score: {:.2f}".format(app.get_current_img_rating()))

            if ENABLE_DEBUGGING:
                cv2.imshow('img', img)
                # Stop if escape key is pressed
                k = cv2.waitKey(30) & 0xff
                if k == 27:
                    break
        # Release the VideoCapture object
    except KeyboardInterrupt():
        sys.exit()


def rotate_screen():

    iterations_for_shake = 5
    shake_iterations = 0
    delta_x = 0 
    x_old = None

    while not quitting.is_set():
        shake_iterations += 1
        gyro: Gyroscope = rotation.read_gyroscope()
        x_old_real = gyro.acceleration_xout
        if x_old is not None : 
            x_old_real = x_old
        delta_x += abs(abs(gyro.acceleration_xout) - abs(x_old_real))
        x_old = gyro.acceleration_xout

        if shake_iterations >= iterations_for_shake and delta_x > 15000 :
            app.show_next_img()
            shake_iterations = 0
            print("shooketh")
            delta_x = 0
        elif shake_iterations >= iterations_for_shake:
            delta_x = 0
            
        
        #rotation.rotate_screen(rotation.read_gyroscope(), app)
        
        time.sleep(.05)


if __name__ == "__main__":

    # attempt picap initialization
    sensor = None
    if RUNS_ON_RPI:
        try:
            sensor = MPR121.begin()
        except Exception as e:
            print(e)
            sys.exit(1)

        # set the thresholds
        sensor.set_touch_threshold(touch_threshold)
        sensor.set_release_threshold(release_threshold)

    # start ui thread
    app.start()

    # wait for app initialization
    while not app.initialized:
        time.sleep(0.1)

    t1 = Thread(target=face_detection)
    t1.start()
    t2 = Thread(target=rotate_screen)
    t2.start()
    t3 = Thread(target=hand_tracking, args=(video_getter, quitting, app))
    t3.start()

    t1.join()
    t2.join()
    t3.join()
    app.join()
