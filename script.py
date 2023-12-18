import time
import pygame
import logging
import g923
import serial
# Disable video driver
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

logging.basicConfig(level=logging.DEBUG)

target_packet_rate_hz = 500

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
        ser = serial.Serial('/dev/serial0',
                        baudrate=400000,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE)
    except:
        logging.error("Failed to open serial port")
        ser = None
        
    controller = None
    done = False
    last_packet_sent_time = time.time()
    last_log_time = time.time()
    measured_packet_rate = 0
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
            if time.time() - last_log_time > 1:
                last_log_time = time.time()
                logging.info(f"Throttle: {int((controller.get_combined_throttle()*500) + 1500)}, Steering: {int((controller.get_steering()*500) + 1500)}, Packet rate: {measured_packet_rate} Hz")
            wait_time = (1/target_packet_rate_hz) - (time.time() - last_packet_sent_time)
            if wait_time > 0:
                time.sleep(wait_time)
            if crsf_frame == None or ser == None:
                continue
            throttle_value = int((controller.get_combined_throttle()*500) + 1500)
            steering_value = int((controller.get_steering()*500) + 1500)
            frame = crsf_build_frame(
                PacketsTypes.RC_CHANNELS_PACKED,
                {"channels": [throttle_value, steering_value]},)
            ser.write(frame)
            measured_packet_rate = 1/(time.time() - last_packet_sent_time)
            last_packet_sent_time = time.time()
        
            
    
if __name__ == '__main__':
    main()