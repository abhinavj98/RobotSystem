import sys
sys.path.insert(0, "./lib/")
import sys
import time
from lib.picarx_improved import *

def parallel_park(px, side):
    #go forward
    #steer 45 and back
    # go forward
    angle = 45
    if(side == 'l'):
        angle = angle*-1
    px.set_dir_servo_angle(0)
    px.forward(50)
    time.sleep(0.5)
    px.set_dir_servo_angle(angle)
    time.sleep(0.2)
    px.backward(50)
    time.sleep(1.15)
    px.set_dir_servo_angle(-angle)
    time.sleep(0.2)
    px.backward(50)
    time.sleep(0.5)
    px.set_dir_servo_angle(0)
    time.sleep(0.2)
    px.forward(50)
    time.sleep(0.5)
    px.stop()
    

def k_turn(px, side):
    #forward at 30 till perp
    #back at -30 till semi perp
    #forward at 30 and whoosh
    angle = 30
    if side == "l":
        angle = angle*-1
    px.set_dir_servo_angle(angle)
    px.forward(50)
    time.sleep(1.5)
    px.set_dir_servo_angle(-angle)
    time.sleep(0.2)
    px.backward(50)
    time.sleep(1)
    px.set_dir_servo_angle(angle)
    time.sleep(0.2)
    px.forward(50)
    time.sleep(0.75)
    px.set_dir_servo_angle(0)
    px.forward(50)
    time.sleep(0.5)
    px.stop()

#2.8.2
if __name__ == "__main__":
    keystroke = 'a'
    px = Picarx()
    time.sleep(1)
    while(keystroke != 'q'):
        keystroke = input("Forward: f,Backward: b, Parking: p, Turn: t, Quit: q \n")
        if(keystroke == 'f'):
            px.forward(50)
            time.sleep(1)
            px.stop()
        elif(keystroke == 'b'):
            px.backward(50)
            time.sleep(1)
            px.stop()
        elif(keystroke == 'p'):
            side = input('Left: l, Right: r \n')
            parallel_park(px,side)
        elif(keystroke == 't'):
            side = input('Left:l, Right:r \n')
            k_turn(px,side)



