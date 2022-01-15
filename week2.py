import sys
import time
sys.path.insert(0, "./lib/")

from lib.picarx_improved import *

def parallel_park(px):
    #go forward
    #steer 45 and back
    # go forward
    px.set_dir_servo_angle(0)
    px.forward(50)
    time.sleep(0.5)
    px.set_dir_servo_angle(-45)
    time.sleep(0.2)
    px.backward(50)
    time.sleep(1.15)
    px.set_dir_servo_angle(45)
    time.sleep(0.2)
    px.backward(50)
    time.sleep(0.5)
    px.set_dir_servo_angle(0)
    time.sleep(0.2)
    px.forward(50)
    time.sleep(0.5)
    px.stop()
    

def k_turn(px):
    #forward at 30 till perp
    #back at -30 till semi perp
    #forward at 30 and whoosh
    px.set_dir_servo_angle(30)
    px.forward(50)
    time.sleep(1.25)
    px.set_dir_servo_angle(-30)
    time.sleep(0.2)
    px.backward(50)
    time.sleep(1)
    px.set_dir_servo_angle(0)
    time.sleep(0.2)
    px.forward(50)
    time.sleep(0.7)
    px.set_dir_servo_angle(30)
    time.sleep(0.2)
    px.forward(50)
    time.sleep(0.65)
    px.stop()

#2.8.2
if __name__ == "__main__":
    keystroke = 'a'
    px = Picarx()
    time.sleep(1)
    k_turn(px)
    # while(keystroke != 'q'):
    #     keystroke = input("F, B, L, R, C, D")
    #     print(keystroke)
    #     if(keystroke == 'f'):
    #         px.forward(50)
    #     elif(keystroke == 'b'):
    #         px.backward(50)
    #     elif(keystroke == 'l'):#park left
    #         px.backward(50)
