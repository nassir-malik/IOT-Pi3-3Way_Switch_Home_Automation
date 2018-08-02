import time
import Adafruit_ADS1x15

import fauxmo
import logging
import time
import sys
import RPi.GPIO as GPIO ## Import GPIO library
 
from debounce_handler import debounce_handler

logging.basicConfig(level=logging.DEBUG)
#GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setmode(GPIO.BCM) ## Use board pin numbering
#Add addtionl pin number for GPIOs
gpio_list = [23,24]
GPIO.setup(gpio_list, GPIO.OUT)

class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """
    TRIGGERS = {"kitchen": 52000,"living room":51000}

    def act(self, client_address, state, name):
        print("State", state, "from client @", client_address)
        
        if name=="kitchen":
            relay_state = GPIO.input(gpio_list[0])
            device_state = self.get_sensor_state(0)
            if state!=device_state:
                GPIO.output(gpio_list[0], not relay_state)
                    
        elif name =="living room":
            relay_state = GPIO.input(gpio_list[1])
            device_state = self.get_sensor_state(2)
            if state!=device_state:
                GPIO.output(gpio_list[1], not relay_state) 

        else:
            print("Device not found!")
        #GPIO.cleanup()
        return True
 
    def get_sensor_state(self, analog_channel):
        adc = Adafruit_ADS1x15.ADS1115()
        GAIN = 1
        state=False

        # Read all the ADC channel values in a list.
        values = [0]*50
        for i in range(50):
            #values[i] = adc.read_adc(0, gain=GAIN)
            values[i] = adc.read_adc(analog_channel, gain=GAIN)-13022
        
        if max(values)>0:
            print("Device is True")
            print(max(values))
            state=True
        else:
            print("Device is False")
            print(max(values))
            state=False
 
        return state
        
if __name__ == "__main__":
    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)
 
    # Register the device callback as a fauxmo handler
    d = device_handler()
    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)
 
    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            time.sleep(0.1)
        except Exception as e:
            logging.critical("Critical exception: "+ e.args  )
            break

