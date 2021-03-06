import sys
sys.path.insert(0, "./lib/")
import time
from lib.picarx_improved import *
import datetime
import logging
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
from utils import run_command
import math
def region_of_interest(edges):
    """Crops image to focus only on bottom half"""
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # only focus bottom half of the screen
    polygon = np.array([[
        (0, height * 1 / 2),
        (width, height * 1 / 2),
        (width, height),
        (0, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    return cropped_edges

def detect_mask(frame):
    """Detect blue line from image"""    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 90, 50])
    upper_blue = np.array([120, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    return mask

def detect_lane(frame):
    """Crops image to the bottom half and makes a  contour around the mask - Center of contour needs to be followed"""
    mask = detect_mask(frame)
    cropped_mask = region_of_interest(mask)
    output = cv2.bitwise_and(frame, frame, mask=mask)
    blurred = cv2.GaussianBlur(cropped_mask, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key = cv2.contourArea)
    x,y,w,h = cv2.boundingRect(c)
    print(x,y,w,h)
    # draw the biggest contour (c) in green
    cv2.circle(output,(int(x+w/2),int(y+h/2)),2,(0,255,0),4)
    cv2.imshow("cropped_image", output)
    return int(x+w/2), int(y+h/2)



if __name__ == "__main__":
    camera = PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 24
    camera.image_effect = "none"  #"none","negative","solarize","emboss","posterise","cartoon",
    rawCapture = PiRGBArray(camera, size=camera.resolution)  

    power_val = 0
    px = Picarx()
    px.set_camera_servo2_angle(-30)
    i=0
    px_power = 40
    time.sleep(2)
    try:
        while True:
            for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):# use_video_port=True
                try:
                    img = frame.array
                    x,y = detect_lane(img)
                    k = cv2.waitKey(1)
                    len_x, len_y = img.shape[1], img.shape[0]
                    #Calculate steering angle by finding the angle in degrees between center of frame wrt detected center of line
                    steering_angle = math.degrees(math.atan((len_x/2-x)/(len_y - y)))/4
                    if(abs(steering_angle)>40):
                        steering_angle = steering_angle/abs(steering_angle)*40
                    print(steering_angle)
                    px.set_dir_servo_angle(-steering_angle)
                except ValueError:
                    steering_angle = 0
                px.forward(px_power - abs(steering_angle)/4)
                rawCapture.truncate(0)

            # run_command(a_t)

            # Vilib.shuttle_button() 
            camera = PiCamera()
            camera.resolution = (640,480)
            camera.framerate = 24
            camera.image_effect = "none"  #"none","negative","solarize","emboss","posterise","cartoon",
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
    finally:
        px.stop()
        camera.close()
