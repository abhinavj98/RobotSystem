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
        
class Sensor(object):
    """Producer function for grayscale module"""
    def __init__(self, bus, delay = 0.2, max = 1500, min = 750):
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")
        self.max =  max
        self.min = min
        self.bus = bus

    def get_grayscale_data(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())
        for j,i in enumerate(adc_value_list):
            if i > self.max:
                adc_value_list[j]=self.max
            elif i < self.min:
                adc_value_list[j] = self.min
        
        self.bus.write(adc_value_list)

    def steering_angle(self):
        pass
    
    def calibrate(self):
        data = self.get_grayscale_data()
        self.ref = sum(data)/len(data)
        return self.ref

class Interpretor():
    """Consumer-Producer function to read sensor data and produce location wrt line"""
    def __init__(self, gm, bus, sensitivity = 0.5, delay = 0.2, target = 'light'):
        self.gm = gm
        self.loc = 0
        self.sensititvity = sensitivity
        self.bus = bus
        self.target = target
    
    def get_location(self):
        data = self.gm.bus.read()
        #Uses the readings to calculate orientation of robot wrt line
        loc = (0.6*(data[2] - data[0])/data[1] + 0.4*self.loc)*self.sensititvity
        if self.target == 'dark':
            loc = loc*-1

        self.loc = loc
        self.bus.write(loc)

        return loc
    
class Controller():
    """Consumer function that reads location and controls the motors"""
    def __init__(self, px_power, delay = 0.2):
        self.px = Picarx()
        self.px_power = px_power
    def forward(self):
        steering_angle = control_bus.read()*40
        self.px.set_dir_servo_angle(steering_angle)
        self.px.forward(self.px_power - abs(steering_angle)/4) 
if __name__=='__main__':
  
  try:
    gm_bus = Bus([0,0,0])
    control_bus = Bus(0) 

    gm = Sensor(gm_bus)
    interpret = Interpretor(gm, control_bus, 1)
    p_control = Controller(40)
    while True:
        gm.get_grayscale_data()
        interpret.get_location()
        p_control.forward()
       
        #time.sleep(0.01)
  finally:
      p_control.px.stop()
