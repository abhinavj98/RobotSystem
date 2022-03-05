!/usr/bin/python3
# coding=utf8
import sys
import cv2
import time
import threading
import numpy as np
import HiwonderSDK.yaml_handle as yaml_handle
import math
import HiwonderSDK.Misc as Misc
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board

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

        return img, valid, areaMaxContour

class motion():
    """Class to control arm movement and corresponding kinematics"""
    def __init__(self, size):
        self.size = size
        self.last_x = 0
        self.last_y = 0
        self.center_list = []
        self.t1 = 0
        self.init()
        self.start()
        th = threading.Thread(target=self.__MoveThread)
        th.setDaemon(True)
        th.start()

    def init(self):
        print("ColorSorting Init")
        initMove()

    def start():
        self.__isRunning = True
        print("ColorSorting Start")

    def __MoveThread(self):
        """Thread which runs armIK parallely"""
        AK = ArmIK()
        servo1 = 500

        coordinate = {
        'red':   (-15 + 0.5, 12 - 0.5, 1.5),
        'green': (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        world_X, world_Y = 0,0
       
        detect_color = 'red'
        while True:
            rect = self.rect
            if self.__isRunning:        
                if detect_color != 'None' and self.start_pick_up:  #如果检测到方块没有移动一段时间后，开始夹取
                    #移到目标位置，高度6cm, 通过返回的结果判断是否能到达指定位置
                    #如果不给出运行时间参数，则自动计算，并通过结果返回
                    set_rgb(detect_color)
                    setBuzzer(0.1)
                    result = AK.setPitchRangeMoving((world_X, world_Y, 7), -90, -90, 0)  
                    if result == False:
                        unreachable = True
                    else:
                        unreachable = False
                        time.sleep(result[2]/1000) #如果可以到达指定位置，则获取运行时间

                        if not self.__isRunning:
                            continue
                        servo2_angle = getAngle(world_X, world_Y, rotation_angle) #计算夹持器需要旋转的角度
                        Board.setBusServoPulse(1, servo1 - 280, 500)  # 爪子张开
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)
                        
                        if not self.__isRunning:
                            continue
                        AK.setPitchRangeMoving((world_X, world_Y, 1.5), -90, -90, 0, 1000)
                        time.sleep(1.5)

                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(1, servo1, 500)  #夹持器闭合
                        time.sleep(0.8)

                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(2, 500, 500)
                        AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 1000)  #机械臂抬起
                        time.sleep(1)

                        if not self.__isRunning:
                            continue
                        result = AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], 12), -90, -90, 0)   
                        time.sleep(result[2]/1000)
                        
                        if not self.__isRunning:
                            continue                   
                        servo2_angle = getAngle(coordinate[detect_color][0], coordinate[detect_color][1], -90)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)

                        if not self.__isRunning:
                            continue
                        AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], coordinate[detect_color][2] + 3), -90, -90, 0, 500)
                        time.sleep(0.5)
                        
                        if not self.__isRunning:
                            continue                    
                        AK.setPitchRangeMoving((coordinate[detect_color]), -90, -90, 0, 1000)
                        time.sleep(0.8)

                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(1, servo1 - 200, 500)  # 爪子张开  ，放下物体
                        time.sleep(0.8)

                        if not self.__isRunning:
                            continue
                        AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], 12), -90, -90, 0, 800)
                        time.sleep(0.8)

                        initMove()  # 回到初始位置
                        time.sleep(1.5)

                        detect_color = 'None'
                        get_roi = False
                        self.start_pick_up = False
                        set_rgb(detect_color)
            else:
                if self._stop:
                    self._stop = False
                    Board.setBusServoPulse(1, servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)
    
    def GetCoordinatesFromContour(self, areaMaxContour):
        """Get real world coordinates from contours"""
        size = self.size
        rect = cv2.minAreaRect(areaMaxContour)
        self.rect = rect
        box = np.int0(cv2.boxPoints(rect))
        roi = getROI(box) 
        get_roi = True
        img_centerx, img_centery = getCenter(rect, roi, size, square_length)
        
        world_x, world_y = convertCoordinate(img_centerx, img_centery, size) 
        return world_x, world_y

    def StartPickUp(self, areaMaxContour):
        """Combines all functions to start pick up s"""
        world_x, world_y = self.GetCoordinatesFromContour(areaMaxContour)
        distance = math.sqrt(pow(world_x - self.last_x, 2) + pow(world_y - self.last_y, 2)) #Compare the last coordinates to determine whether to move
        self.last_x, self.last_y = world_x, world_y   
        
        if distance < 0.5:
            count += 1
            self.center_list.extend((world_x, world_y))
            if self.start_count_t1:
                self.start_count_t1 = False
                self.t1 = time.time()
            if time.time() - self.t1 > 1:
                self.start_count_t1 = True
                self.world_X, self.world_Y = np.mean(np.array(self.center_list).reshape(count, 2), axis=0)
                self.center_list = []
                count = 0
                self.start_pick_up = True
        else:
            self.t1 = time.time()
            self.start_count_t1 = True
            self.center_list = []
            count = 0

def load_config():
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    return lab_data

def initMove():
    servo1 = 500
    Board.setBusServoPulse(1, servo1 - 50, 300)
    Board.setBusServoPulse(2, 500, 500)
    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)

#设置扩展板的RGB灯颜色使其跟要追踪的颜色一致
def set_rgb(color):
    if color == "red":
        Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
        Board.RGB.show()
    elif color == "green":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
        Board.RGB.show()
    elif color == "blue":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
        Board.RGB.show()
    else:
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
        Board.RGB.show()
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
    size = (640,480)
    percept_arm = perception(__target_color, size, range_rgb) 
    cap = cv2.VideoCapture(-1)
    time.sleep(3)
    #Create motion object
    arm = motion(size)
    
    while True:
        ret,img = cap.read()
        if ret:
            frame = img.copy()
            #Find color and make bounding boxes on frames, get max contour bbox
            Frame, valid, areaMaxContour = percept_arm.FindColor(frame)
            if valid:
                """If max contour bbox is valid start pickup"""
                arm.StartPickUp(areaMaxContour)
            frame_resize = cv2.resize(Frame, (320, 240))
            cv2.imshow('frame', frame_resize)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    cv2.destroyAllWindows()
