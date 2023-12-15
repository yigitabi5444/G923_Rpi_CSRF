import pygame
import logging
import g923
import time

logging.basicConfig(level=logging.DEBUG)

try:
    import pigpio
    logging.info("Loaded pigpio library")
except ImportError as e:
    logging.warn("Failed to load pigpio library, running in debug mode")
    pigpio = None
    
def print_joystick_axis_data(joystick:pygame.joystick.JoystickType):
    logging.info("")
    logging.info("")
    logging.info("")
    logging.info("")
    logging.info("")
    logging.info("")
    for i in range(joystick.get_numaxes()):
        logging.info("Axis %d: %f" % (i, joystick.get_axis(i)))
    for i in range(joystick.get_numbuttons()):
        logging.info("Button %d: %d" % (i, joystick.get_button(i)))
    for i in range(joystick.get_numhats()):
        logging.info("Hat %d: %s" % (i, str(joystick.get_hat(i))))
    time.sleep(0.1)
    
def print_joystick_info():
    logging.info("Gas Pedal: %f, Brake Pedal: %f, Steering Wheel: %f" % (gas_pedal, brake_pedal, steering_wheel))

def main():
    pygame.init()
    joystick = None
    
    done = False
    while not done:
        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.

            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
                if event.button == 0:
                    if joystick.rumble(0, 0.7, 500):
                        print(f"Rumble effect played on joystick {event.instance_id}")

            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                joystick = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joystick
                print(f"Joystick {event.instance_id} disconnected")
        
        if joystick is not None:
            print_joystick_axis_data(joystick)
            
    
if __name__ == '__main__':
    main()