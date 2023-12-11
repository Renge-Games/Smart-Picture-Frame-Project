#!/usr/bin/python3
# -*- coding: utf-8 -*-

from threading import Event, Thread

import cv2
import mediapipe as mp

from settings import *
from VideoGet import VideoGet

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils


hasSwitched = False
quitting: Event = None
app = None


def draw_hand_connections(img, results):
    """Drawing landmark connections"""

    global hasSwitched
    global app

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id_, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                INDEX_TIP = 8
                if id_ == INDEX_TIP:
                    print(id_, cx, cy)
                    if cx < HAND_LEFT:
                        if not hasSwitched and app is not None:
                            app.show_prev_img()
                        hasSwitched = True
                    elif cx > HAND_RIGHT:
                        if not hasSwitched and app is not None:
                            app.show_next_img()
                        hasSwitched = True
                    else:
                        hasSwitched = False

            if ENABLE_DEBUGGING:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
        return img


def process_image(img):
    """Processing the input image"""
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(gray_image)
    #print(results.multi_hand_landmarks)
    return results


def hand_tracking(video, quit_flag, application):
    global hasSwitched
    global app
    global video_getter
    global quitting

    app = application
    video_getter = video
    quitting = quit_flag

    hasSwitched = False
    while not quitting.is_set():
        image = video_getter.frame

        results = process_image(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        draw_hand_connections(image, results)


if __name__ == "__main__":
    video_getter = VideoGet(0).start()
    quitting = Event()
    Thread(target=hand_tracking, args=(video_getter, quitting, None)).start()

    while not quitting.is_set():
        if (cv2.waitKey(1) == ord("q")) or video_getter.stopped:
            video_getter.stop()
            quitting.set()

        cv2.imshow("Hand tracking", video_getter.frame)
    print("exiting program")
