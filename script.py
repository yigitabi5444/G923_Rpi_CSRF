import pygame
import logging
import g923
import serial
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
    
def map_to_int(value:float, in_min:float, in_max:float, out_min:int, out_max:int):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    
try:
    from crsf_parser.payloads import PacketsTypes
    from crsf_parser import crsf_frame
    from crsf_parser.handling import crsf_build_frame
except ImportError as e:
    logging.warn("Failed to load crsf_parser library, running in debug mode")
    crsf_frame = None
    crsf_build_frame = None
    PacketsTypes = None
    
def main():
    pygame.init()
    try:
        ser = serial.Serial('dev/serial1',
                        baudrate=425000,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE)
    except:
        logging.error("Failed to open serial port")
        ser = None
        
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
            if crsf_frame == None or ser == None:
                continue
            throttle_value = map_to_int(controller.get_combined_throttle(), -1, 1, 1000, 2000)
            steering_value = map_to_int(controller.get_steering(), -1, 1, 1000, 2000)
            frame = crsf_build_frame(
                PacketsTypes.RC_CHANNELS_PACKED,
                {"channels": [throttle_value, steering_value, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]},)
            ser.write(frame)
        
            
    
if __name__ == '__main__':
    main()