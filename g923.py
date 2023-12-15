import pygame
import logging
import time

try:
    import evdev
    logging.info("Loaded evdev library")
except ImportError as e:
    logging.warning("Failed to evdev library, disabling evdev support")
    evdev = None

GAS_PEDAL_AXIS = 2
BRAKE_PEDAL_AXIS = 3
STEERING_AXIS = 0
CLUTCH_PEDAL_AXIS = 1
X_BUTTON = 0
SQUARE_BUTTON = 1
CIRCLE_BUTTON = 2
TRIANGLE_BUTTON = 3
R1 = 4
L1 = 5
R2 = 6
L2 = 7
SHARE = 8
OPTIONS = 9
R3 = 10
L3 = 11
ROTARY_DIAL_CW = 21
ROTARY_DIAL_CCW = 22
PLUS = 19
MINUS = 20
ENTER = 23
PS = 24

class G923:
    joystick:pygame.joystick.JoystickType
    def __init__(self, joystick):
        self.joystick = joystick
        if evdev != None:
            device = evdev.InputDevice('/dev/input/event1')
            print(device)
            print(device.capabilities(verbose=True))
    
    def get_button(self, button):
        if self.joystick == None:
            return False
        return self.joystick.get_button(button)
    
    def get_gas_pedal(self):
        if self.joystick == None:
            return 0
        value = self.joystick.get_axis(GAS_PEDAL_AXIS)
        value = (1-value)/2
        return value
    
    def get_brake_pedal(self):
        if self.joystick == None:
            return 0
        value = self.joystick.get_axis(BRAKE_PEDAL_AXIS)
        value = (1-value)/2
        return value
    
    def get_combined_throttle(self):
        if self.joystick == None:
            return 0
        return self.get_gas_pedal() - self.get_brake_pedal()
    
    def get_steering(self):
        if self.joystick == None:
            return 0
        return self.joystick.get_axis(STEERING_AXIS)
    
    def print_data(self):
        logging.info("Gas pedal: %f" % (self.get_gas_pedal()*100))
        logging.info("Brake pedal: %f" % (self.get_brake_pedal()*100))
        logging.info("Combined throttle: %f" % (self.get_combined_throttle()*100))
        logging.info("Steering: %f" % (self.get_steering()*100))
        time.sleep(0.2)