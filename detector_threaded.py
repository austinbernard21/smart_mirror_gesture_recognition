######## Raspberry Pi Camera Live Hand Gesture Tracking #########
#
# Author: Austin Bernard
# Date: 4/22/2021
# Description: This code is a multithreaded application to run an object detection and gesture classification
# pipeline using opencv Haar cascades and a Tensorflow lite model trained using transfer learning.
# This code should work on a raspberry pi with a Camera attached. Depending on what camera is used, you may
# have to change the cv2.VideoCapture parameter to 0 or 1
#
# Tensorflow lite inferenece code based off of this resource:
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py


import cv2
import numpy as np
import tensorflow as tf
import time
from threading import Thread

# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(450,300),framerate=30):
        # Initialize the PiCamera and the camera image stream
        # May have to change to 0 or 1 depending on camera used
        self.stream = cv2.VideoCapture(1)
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


# Define interpreter for TF lite
interpreter = tf.lite.Interpreter('base_model.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_shape = input_details[0]['shape']

# Define our trained Haar classifier
cascade = cv2.CascadeClassifier('cascades1/cascade.xml')

# Initialize video stream
videostream = VideoStream(resolution=(450,300),framerate=30).start()
time.sleep(1)


while True:
    # Grab frame from video stream
    frame = videostream.read()

    # Convert to gray for easier manipulations on images
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use Haar classifier to detect hands
    hands = cascade.detectMultiScale(gray,minNeighbors=5,minSize=(150,150))

    # If more than one detections, choose first. MinNeighbors and minSize in above function, along
    # with how the model is trained should limit this being a problem
    if len(hands) >= 1:
        hand_example = hands[0]
        # Grab coordinates of detected hand
        (x_cord, y_cord, width, height) = hand_example

        # print(f'x : {x_cord}, y: {y_cord}, width: {width}, height: {height}')
        center = (x_cord + width//2, y_cord + height//2)  

        # Draw rectangle on hand
        gray = cv2.rectangle(gray, (x_cord,y_cord), (x_cord+width,y_cord+height),(0.255,0),3)

        # Get hand image and resize for tensorflow classifier
        crop = cv2.resize(frame[y_cord:y_cord+height,x_cord:x_cord+width],(160,160))

        # Run classifier
        interpreter.set_tensor(input_details[0]['index'], crop.reshape(1,160,160,3).astype('float32'))
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])


    # Show frame in grayscale
    cv2.imshow('test', gray)

    # Press 'esc' to quit
    if cv2.waitKey(1) == 27:
        break

# Stop stream and close windows
cv2.destroyAllWindows()
videostream.stop()