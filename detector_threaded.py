######## Raspberry Pi Camera Live Hand Gesture Tracking #########
#
# Author: Austin Bernard
# Date: 4/22/2021
# Description: This code is a multithreaded application to capture real time video streams
# and use a custom tensorflow trained hand gesture detector to track 3 hand gestures, open, close, and pointing
# and maps these to mouse controls like scroll, drag, and click respectively
#
# Baseline code if based off of Evan Juras Webcam Object Detection Using Tensorflow-trained Classifier
# link to his code is here https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/TFLite_detection_webcam.py
#
# Tensorflow lite inferenece code based off of this resource:
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py


import cv2
import numpy as np
import time
import pyautogui
from threading import Thread
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(640,480),framerate=30):
        # Initialize the PiCamera and the camera image stream
        # May have to change to 0 or 1 depending on camera used
        self.resolution = resolution
        self.stream = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

	# Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
	# Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
	# Return the most recent frame
        return self.frame

    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True

    def get_resolution(self):
        return self.resolution


def run_detector():

    # Define model
    hands = mp_hands.Hands(model_complexity=0,
                           min_detection_confidence=0.5,
                           min_tracking_confidence=0.5)

    # Initialize video stream
    videostream = VideoStream(framerate=30).start()
    time.sleep(1)

    (screenx, screeny) = pyautogui.size()

    x_mouse = 0
    y_mouse = 0

    while True:
        # Grab frame from video stream
        image = videostream.read()

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_width, image_height, _ = image.shape
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                x_mouse = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width)
                y_mouse = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height)

            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))


        transformed_coordx = (x_mouse * screenx) / videostream.get_resolution()[1]
        # for inverted x coordinate
        transformed_coordx = (screenx - transformed_coordx)
        transformed_coordy = (y_mouse * screeny) / videostream.get_resolution()[0]

        pyautogui.moveTo(transformed_coordx, transformed_coordy)
            

        # Show frame
        # cv2.imshow('test', frame)

        # Press 'esc' to quit
        if cv2.waitKey(1) == 27:
            break

    # Stop stream and close windows
    cv2.destroyAllWindows()
    videostream.stop()

# run_detector()