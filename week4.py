import sys
sys.path.insert(0, "./lib/")
from lib.picarx_improved import *
import time
# from utils import reset_mcu
# reset_mcu()
# from grayscale_module import Grayscale_Module
# from adc import ADC
class Bus():
    def __init__(self, default):
        self.message = default

    def read(self):
        return self.message
    
    def write(self, message):
        self.message = message
        
class Grayscale_Module(object):
    def __init__(self, bus, max = 1500, min = 750, target = 'light', sensititvity = 0.5):
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")
        self.max =  max
        self.min = min
        self.sensititvity = sensititvity
        self.target = target
        self.bus = bus

    def get_grayscale_data(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())
        self.bus.write(adc_value_list)

    def steering_angle(self):
        pass
    
    def calibrate(self):
        data = self.get_grayscale_data()
        self.ref = sum(data)/len(data)
        return self.ref

class Controller():
    def __init__(self, gm, bus):
        self.gm = gm
        self.loc = 0
        self.bus = bus
    
    def get_location(self):
        data = self.gm.bus.read()
        for j,i in enumerate(data):
            if i > self.gm.max:
                data[j]=self.gm.max
            elif i < self.gm.min:
                data[j] = self.gm.min
        #Uses the readings to calculate orientation of robot wrt line
        loc = (0.6*(data[2] - data[0])/data[1] + 0.4*self.loc)*gm.sensititvity
        if gm.target == 'dark':
            loc = loc*-1

        self.loc = loc
        self.bus.write(loc)

        return loc
    

if __name__=='__main__':
  px = Picarx()
  try:
    gm_bus = Bus([0,0,0])
    control_bus = Bus(0) 
    gm = Grayscale_Module(gm_bus)
    p_control = Controller(gm, control_bus)
    px_power = 40
    while True:
        steering_angle = control_bus.read()*40
        px.set_dir_servo_angle(steering_angle)
        px.forward(px_power - abs(steering_angle)/4) 
        #time.sleep(0.01)
  finally:
      px.stop()
