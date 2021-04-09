import numpy as np
import cv2
import tensorflow as tf
import time

interpreter = tf.lite.Interpreter('base_model.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_shape = input_details[0]['shape']


cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)

cascade = cv2.CascadeClassifier('cascades1/cascade.xml')

# used to record the time when we processed last frame
prev_frame_time = 0
  
# used to record the time at which we processed current frame
new_frame_time = 0

while True:
    ret, img = cam.read()
    img = cv2.resize(img, (450,300))
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # print(img.shape)
    hands = cascade.detectMultiScale(gray,minNeighbors=5,minSize=(30,30))
    # print('here is a hand array:', hands)
    if len(hands) >= 1:
        hand_example = hands[0]
        (x_cord, y_cord, width, height) = hand_example
        # print(f'x : {x_cord}, y: {y_cord}, width: {width}, height: {height}')
        center = (x_cord + width//2, y_cord + height//2)   
        gray = cv2.rectangle(gray, (x_cord,y_cord), (x_cord+width,y_cord+height),(0.255,0),3)
        crop = cv2.resize(img[y_cord:y_cord+height,x_cord:x_cord+width],(160,160))
        # print(crop.shape)
        interpreter.set_tensor(input_details[0]['index'], crop.reshape(1,160,160,3).astype('float32'))
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        # print(output_data)
        # time.sleep(0.08)
    # for (x,y,w,h) in hands:
    #     center = (x + w//2, y + h//2)   
    #     img = cv2.rectangle(img, (x,y), (x+w,y+h),(0.255,0),3)
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    fps = int(fps)
    print(fps)

    cv2.imshow('test',gray)

        
    if cv2.waitKey(1) == 27:
        break
            
    
    
cam.release()
cv2.destroyAllWindows()