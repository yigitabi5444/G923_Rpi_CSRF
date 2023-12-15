import pygame
import logging
import g923

logging.basicConfig(level=logging.DEBUG)

try:
    import pigpio
    logging.info("Loaded pigpio library")
except ImportError as e:
    logging.warn("Failed to load pigpio library, running in debug mode")
    pigpio = None
    
#Steering Wheel [-1, 1]
#Gas Pedal [0, 1]
#Brake Pedal [0, 1]
global gas_pedal, brake_pedal, steering_wheel 

def get_joystick_data(joystick:pygame.joystick.JoystickType):
    global gas_pedal, brake_pedal, steering_wheel 
    gas_pedal = joystick.get_axis(g923.GAS_PEDAL_AXIS)
    brake_pedal = joystick.get_axis(g923.BRAKE_PEDAL_AXIS)
    steering_wheel = joystick.get_axis(g923.STEERING_AXIS)
    
def print_joystick_info():
    logging.info("Gas Pedal: %f, Brake Pedal: %f, Steering Wheel: %f" % (gas_pedal, brake_pedal, steering_wheel))

def main():
    pygame.init()
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        logging.error("No joysticks found")
        return
    joystick = pygame.joystick.Joystick(0)
    joystick_name = joystick.get_name()
    logging.info("Found joystick: %s" % joystick_name)
    joystick.init()
    
    while True:
        get_joystick_data(joystick)
        print_joystick_info()
            
    
if __name__ == '__main__':
    main()