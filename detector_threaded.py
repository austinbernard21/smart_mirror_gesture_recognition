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
from tflite_runtime.interpreter import Interpreter
from threading import Thread

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

    # Path to label map file
    PATH_TO_LABELS = 'label_map.pbtxt'

    # Load the label map
    with open(PATH_TO_LABELS, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    if labels[0] == '???':
        del(labels[0])

    # Define interpreter for TF lite
    interpreter = Interpreter('detect.tflite')
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_shape = input_details[0]['shape']

    input_mean = 127.5
    input_std = 127.5


    # Initialize video stream
    videostream = VideoStream(framerate=30).start()
    time.sleep(1)

    (screenx, screeny) = pyautogui.size()

    imW, imH = videostream.get_resolution()

    min_conf_threshold = .5

    action_map = {'close':'drag','open':'move','point':'click'}
    current_action = action_map['open']

    while True:
        # Grab frame from video stream
        frame = videostream.read()


        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img_resized = cv2.resize(img, (input_shape[1],input_shape[2]))
        input_data = np.expand_dims(img_resized,axis=0)
        input_data = (np.float32(input_data) - input_mean) / input_std

        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects

        highest_score_index = np.argmax(scores)

        score = scores[highest_score_index]
        box = boxes[highest_score_index]
        class_name = classes[highest_score_index]

        if (score > min_conf_threshold) and (score <= 1.0):

            current_action = action_map[labels[int(class_name)]]
            

            ymin = int(max(1,(box[0] * imH)))
            xmin = int(max(1,(box[1] * imW)))
            ymax = int(min(imH,(box[2] * imH)))
            xmax = int(min(imW,(box[3] * imW)))

            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

            # for center circle
            height = ymax - ymin
            width = xmax - xmin
            center_x = xmin + width//2
            center_y = ymin + height//2
            center = (center_x, center_y)
            cv2.circle(frame, center, 5, color=(0,0,255), thickness=-1)

            transformed_coordx = (center[0] * screenx) / videostream.get_resolution()[1]
            # for inverted x coordinate
            transformed_coordx = (screenx - transformed_coordx)
            transformed_coordy = (center[1] * screeny) / videostream.get_resolution()[0]

            if current_action == 'drag':
                pyautogui.mouseDown(transformed_coordx, transformed_coordy)
            elif current_action == 'move':
                pyautogui.mouseUp()
                pyautogui.moveTo(transformed_coordx, transformed_coordy)
            elif current_action == 'click':
                pyautogui.moveTo(transformed_coordx, transformed_coordy)
                pyautogui.click(interval=1) 

            # Draw label
            # object_name = labels[int(class_name)] # Look up object name from "labels" array using class index
            # label = '%s: %d%%' % (object_name, int(score*100)) # Example: 'person: 72%'
            # labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            # label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            # cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            # cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

        # Show frame
        # cv2.imshow('test', frame)

        # Press 'esc' to quit
        if cv2.waitKey(1) == 27:
            break

    # Stop stream and close windows
    cv2.destroyAllWindows()
    videostream.stop()

# run_detector()