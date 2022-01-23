import sys
sys.path.insert(0, "./lib/")
from lib.picarx_improved import *
import time
# from utils import reset_mcu
# reset_mcu()
# from grayscale_module import Grayscale_Module
# from adc import ADC

class Grayscale_Module(object):
    def __init__(self, max = 1500, min = 750, target = 'light'):
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")
        self.max =  max
        self.min = min

    def get_grayscale_data(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())
        return adc_value_list

    def steering_angle(self):
        pass
    
    def calibrate(self):
        data = self.get_grayscale_data()
        self.ref = sum(data)/len(data)
        return self.ref

if __name__=='__main__':
  try:
    gm = Grayscale_Module()
    px = Picarx()
    px_power = 10
    #gm.calibrate()
    while True:
        data = gm.get_grayscale_data()
        for j,i in enumerate(data):
            if i > gm.max:
                data[j]=gm.max
            elif i < gm.min:
                data[j] = gm.min
        print(data)
        print((data[2] - data[0])/data[1])
        time.sleep(1)
  finally:
      px.stop()
