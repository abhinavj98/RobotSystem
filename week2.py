import sys
import time
sys.path.insert(0, "./lib/")

from lib.picarx_improved import *

def parallel_park(px):
    #go forward
    #steer 45 and back
    # go forward
    px.forward(70)
    time.sleep(0.5)
    px.set_dir_servo_angle(45)
    time.sleep(0.2)
    px.backward(70)
    time.sleep(0.5)
    px.forward(70)
    time.sleep(0.2)
    
    

#2.8.2
if __name__ == "__main__":
    keystroke = 'a'
    px = Picarx()
    time.sleep(1)
    parallel_park(px)
    while(keystroke != 'q'):
        keystroke = input("F, B, L, R, C, D")
        print(keystroke)
        if(keystroke == 'f'):
            px.forward(50)
        elif(keystroke == 'b'):
            px.backward(50)
        elif(keystroke == 'l'):#park left
            px.backward(50)