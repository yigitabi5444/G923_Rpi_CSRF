import pygame
import logging
import g923
import time
# Disable video driver
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

logging.basicConfig(level=logging.DEBUG)

try:
    import pigpio
    logging.info("Loaded pigpio library")
except ImportError as e:
    logging.warn("Failed to load pigpio library, running in debug mode")
    pigpio = None
    
def print_joystick_axis_data(joystick:pygame.joystick.JoystickType):
    for i in range(joystick.get_numaxes()):
        logging.info("Axis %d: %f" % (i, joystick.get_axis(i)))
    for i in range(joystick.get_numbuttons()):
        logging.info("Button %d: %d" % (i, joystick.get_button(i)))
    for i in range(joystick.get_numhats()):
        logging.info("Hat %d: %s" % (i, str(joystick.get_hat(i))))
    time.sleep(0.2)
    
def main():
    pygame.init()
    controller = None
    done = False
    while not done:
        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                controller = g923.G923(joy)
                logging.info(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                controller = None
                logging.info(f"Joystick {event.instance_id} disconnected")
        if controller != None:
            controller.print_data()
            
    
if __name__ == '__main__':
    main()