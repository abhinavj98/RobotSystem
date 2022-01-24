import sys
sys.path.insert(0, "./lib/")
import time
from lib.picarx_improved import *
import datetime

import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
from utils import run_command

def detect_edges(frame):
    # filter for blue lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.imshow("hsv", hsv)
    lower_blue = np.array([90, 90, 50])
    upper_blue = np.array([120, 180, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    cv2.imshow("blue mask", mask)

    # detect edges
    edges = cv2.Canny(mask, 200, 400)

    return edges

if __name__ == "__main__":
    camera = PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 24
    camera.image_effect = "none"  #"none","negative","solarize","emboss","posterise","cartoon",
    rawCapture = PiRGBArray(camera, size=camera.resolution)  

    power_val = 0
    px = Picarx()


    try:
        while True:
            for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):# use_video_port=True
                img = frame.array
                edge = detect_edges(img)
                cv2.imshow("edge", edge)
                k = cv2.waitKey(1) & 0xFF
                # 27 is ESC key
                if k == 27:
                    camera.close()
                    continue
                elif k == ord('o'):
                    if power_val <=90:
                        power_val += 10
                        print("power_val:",power_val)  # motor power up
                elif k == ord('p'):
                    if power_val >=10:
                        power_val -= 10
                        print("power_val:",power_val)  # motor power up down
                elif k == ord('w'):
                    px.set_dir_servo_angle(0) # go forward
                    px.forward(power_val) 
                elif k == ord('a'):
                    px.set_dir_servo_angle(-30) # go left
                    px.forward(power_val)
                elif k == ord('s'):
                    px.set_dir_servo_angle(0) # go back
                    px.backward(power_val)
                elif k == ord('d'):
                    px.set_dir_servo_angle(30) # go right
                    px.forward(power_val)
                elif k == ord('f'):    
                    px.stop()  # stop

            
                elif k == ord('t'):   # shoot
                    camera.close()
                    break
                rawCapture.truncate(0)

            print("take a photo wait...")
            picture_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            picture_path = '/home/pi/Pictures/' + picture_time + '.jpg'

            a_t = "sudo raspistill -t 250  -w 2592 -h 1944 " + " -o " + picture_path

            print(a_t)
            run_command(a_t)

            # Vilib.shuttle_button() 
            camera = PiCamera()
            camera.resolution = (640,480)
            camera.framerate = 24
            camera.image_effect = "none"  #"none","negative","solarize","emboss","posterise","cartoon",
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
    finally:
        px.stop()
        camera.close()
