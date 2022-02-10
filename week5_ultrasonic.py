import sys
sys.path.insert(0, "./lib/")
from lib.picarx_improved import *
from RossROS.rossros import *
import logging
logging.getLogger().setLevel(logging.INFO)
from ultrasonic import *
class Sensor(object):
    """Producer function for grayscale module"""
    def __init__(self,  max = 1500, min = 750):
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
        for j,i in enumerate(adc_value_list):
            if i > self.max:
                adc_value_list[j]=self.max
            elif i < self.min:
                adc_value_list[j] = self.min
        return adc_value_list


    def calibrate(self):
        data = self.get_grayscale_data()
        self.ref = sum(data)/len(data)
        return self.ref

class Sensor_us(object):
    def __init__(self, min = 25):
        self.trig_pin = Pin("D2") 
        self.echo_pin = Pin("D3")
        self.ultrasonic = Ultrasonic(self.trig_pin, self.echo_pin)
    
    def get_ultrasonic_data(self):
        distance = self.ultrasonic.read()
        return distance


class Interpretor():
    """Consumer-Producer function to read sensor data and produce location wrt line"""
    def __init__(self, sensitivity = 0.5, delay = 0.2, target = 'light'):
        self.loc = 0
        self.sensititvity = sensitivity
        self.target = target
        self.delay = delay

   
    def get_location(self, data):
        #Uses the readings to calculate orientation of robot wrt line
        loc = (0.6*(data[0][2] - data[0][0])/data[0][1] + 0.4*self.loc)*self.sensititvity
        if self.target == 'dark':
            loc = loc*-1
        self.loc = loc
        distance = data[1]
        stop = 0
        if distance > 0 and distance < 300:
                if distance < 25:
                    stop = 1
                else:
                    stop = 0
        return loc, stop

class Controller():
    """Consumer function that reads location and controls the motors"""
    def __init__(self, px_power):
        self.px = Picarx()
        self.px_power = px_power

    def forward(self, data):
        steering_angle = data[0]*40
        if(data[1] == 1):
            self.px.stop()
        else:
            self.px.set_dir_servo_angle(steering_angle)
            self.px.forward(self.px_power - abs(steering_angle)/4)

if __name__=='__main__':
  
  try:
    gm_sensor = Sensor()
    us_sensor = Sensor_us()
    interpret = Interpretor()
    control = Controller(40)
   
    termination_bus = Bus(False, name = "Termination Bus")
    gm_bus = Bus((0,0,0), name = "Inpu_gm bus")
    us_bus = Bus(0, name = "Input_us bus")
    control_bus = Bus(0, name = "Output bus") 
   
    gm_node = Producer(gm_sensor.get_grayscale_data, gm_bus, termination_busses = termination_bus, name = "Grayscale producer")
    us_node = Producer(us_sensor.get_ultrasonic_data, us_bus, termination_busses = termination_bus, name = "Ultrasonic producer")
    interpret_node = ConsumerProducer(interpret.get_location, input_busses = (gm_bus, us_bus), output_busses = control_bus, termination_busses = termination_bus, name = "Interpretor PC")
    p_control_node = Consumer(control.forward, control_bus, termination_busses = termination_bus, name = "Control consumer") 
    printer_node = Printer(control_bus)
    timer_node = Timer(termination_bus, duration = 0, name = "Timer node", termination_busses = termination_bus)
    
    node_list = [timer_node, gm_node, us_node, interpret_node, p_control_node, printer_node]
    runConcurrently(node_list)
  finally:
    control.px.stop()
