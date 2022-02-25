#!/usr/bin/python3
# coding=utf8
import sys
import cv2
import time
import threading
import numpy as np
import HiwonderSDK.yaml_handle as yaml_handle
import math
import HiwonderSDK.Misc as Misc

class perception():
    """Perception class takes in image frame and makes a bounding box around the target color for the same"""
    def __init__(self, tc, orig_imsize, range_rgb):
        self.__target_color = tc
        self.__orig_imsize = orig_imsize
        self.__range_rgb = range_rgb

    def ConvertFrameToLab(self, img, size = (640,480)):
        """ Takes in an input BGR frame and converts into the LAB format"""
        frame_resize = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert image to LAB space
        return frame_lab

    def FindMaxContoursOfColor(self, color, frame_lab, lab_data):
        """Finds the maximum contour size of a given color"""
        detect_color = color
        frame_mask = cv2.inRange(frame_lab,
                                        (lab_data[detect_color]['min'][0],
                                        lab_data[detect_color]['min'][1],
                                        lab_data[detect_color]['min'][2]),
                                        (lab_data[detect_color]['max'][0],
                                        lab_data[detect_color]['max'][1],
                                        lab_data[detect_color]['max'][2]))  # Do bitwise operations on the original image and mask
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # open operation
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # close operation
        areaMaxContour, area_max = self.GetAreaMaxContour(contours)  # find the largest contour
        return areaMaxContour, area_max

    def ContourIsValid(self, area_max, areaMaxContour, size = (640, 480)):
        """Check if contour is of valid size"""
        if area_max > 1000: # have found the largest area
            (center_x, center_y), radius = cv2.minEnclosingCircle(areaMaxContour) # Get the smallest circumcircle

            center_x = int(Misc.map(center_x, 0, size[0], 0, self.__orig_imsize[1]))
            center_y = int(Misc.map(center_y, 0, size[1], 0, self.__orig_imsize[0]))
            radius = int(Misc.map(radius, 0, size[0], 0, self.__orig_imsize[1]))
            if radius > 100:
                return False, None
            return True, (center_x, center_y)
        else:
            return False, None

    def LabelBox(self, areaMaxContour, img, color):
        """Label the image frame accordint to the maximum contour found"""
        rect = cv2.minAreaRect(areaMaxContour)
        box = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(img, [box], -1, color, 2)
        return box

        # Find the contour with the largest area
    # parameter is a list of contours to compare
    def GetAreaMaxContour(self, contours):
        contour_area_temp = 0
        contour_area_max = 0
        areaMaxContour = None

        for c in contours:  # 历遍所有轮廓
            contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # 只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰
                    areaMaxContour = c

        return areaMaxContour, contour_area_max  # 返回最大的轮廓
    
    def FindColor(self, img):
        """Combining all helper functions to find bounding box for given color"""
        img_copy = img.copy()
        frame_lab = self.ConvertFrameToLab(img_copy)
        for i in lab_data:
            if i in self.__target_color:
                areaMaxContour, area_max = self.FindMaxContoursOfColor(i, frame_lab, lab_data)            
                valid, centers = self.ContourIsValid(area_max, areaMaxContour)
                if not valid:
                    return img
                #Label Box
                box = self.LabelBox(areaMaxContour, img, self.__range_rgb[self.__target_color])

        return img

def load_config():
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    return lab_data


if __name__ == '__main__':

    if sys.version_info.major == 2:
        print("Please run this program with python3!")
        sys.exit(0)
    
    range_rgb = {
        'red': (0, 0, 255),
        'blue': (255, 0, 0),
        'green': (0, 255, 0),
        'black': (0, 0, 0),
        'white': (255, 255, 255),
    }

    lab_data = load_config()
    __target_color = ('red')
    #Create perception object
    percept_arm = perception(__target_color, (640,480), range_rgb) 
    cap = cv2.VideoCapture(-1)
    time.sleep(3)
    
    while True:
        ret,img = cap.read()
        if ret:
            frame = img.copy()
            #Find color and make bounding boxes on frames
            Frame = percept_arm.FindColor(frame)  
            frame_resize = cv2.resize(Frame, (320, 240))
            cv2.imshow('frame', frame_resize)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    cv2.destroyAllWindows()
