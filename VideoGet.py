from threading import Thread
import cv2

# https://nrsyed.com/2018/07/05/multithreading-with-opencv-python-to-improve-video-processing-performance/


class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()
                #self.frame = cv2.flip(self.frame, 1)  # mirror the image

    def stop(self):
        self.stopped = True
