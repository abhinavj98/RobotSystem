import sys
sys.path.insert(0, "./lib/")
from lib.picarx_improved import *
import time
from utils import reset_mcu
reset_mcu()
from grayscale_module import Grayscale_Module
from adc import ADC

class Grayscale_Module(object):
    def __init__(self,ref = 0, target = 'light'):
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")
        self.ref = ref

    def get_grayscale_data(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read()-self.ref)
        adc_value_list.append(self.chn_1.read()-self.ref)
        adc_value_list.append(self.chn_2.read()-self.ref)
        return adc_value_list

    def steering_angle(self):
        
    
    def calibrate(self):
        data = self.get_grayscale_data()
        self.ref = sum(data)/len(data)
        return self.ref

if __name__=='__main__':
  try:
    gm = Grayscale_Module(ref = 0)
    px = Picarx()
    px_power = 10
    gm.calibrate()
    while True:
        print(GM.get_grayscale_data())
        time.sleep(1)
  finally:
      px.stop()