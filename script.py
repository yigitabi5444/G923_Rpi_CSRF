import time
import pygame
import logging
import g923
import serial
# Disable video driver
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

logging.basicConfig(level=logging.DEBUG)

target_packet_rate_hz = 100
steering_deadzone = 0.05

try:
    import pigpio
    logging.info("Loaded pigpio library")
except ImportError as e:
    logging.warn("Failed to load pigpio library, running in debug mode")
    pigpio = None
    

def throtle_curve(x):
    if x != 0:
        sign = x/abs(x)
    else:
        sign = 1
    x = abs(x)
    val = pow(x, 4)*sign
    if val < -1:
        val = -1
    if val > 1:
        val = 1
    return val
    
def steering_curve(x):
    if x != 0:
        sign = x/abs(x)
    else:
        sign = 1
    x = abs(x)
    if x < steering_deadzone:
        val = 0
    else:
        val = pow(x, 0.7)*sign
    if val < -1:
        val = -1
    if val > 1:
        val = 1
    return val
    
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
    frame_size = 0
    last_sent_frame = None
    last_throttle = 0
    last_steering = 0
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
                # Format the bytes of the last frame into a hex string
                last_frame_hex = " ".join("{:02x}".format(c) for c in last_sent_frame)
                logging.info(f"Throttle: {last_throttle}, Steering: {last_steering}, Packet rate: {measured_packet_rate} Hz, Frame size: {frame_size} bytes, Last frame: {last_frame_hex}")
            wait_time = (1/target_packet_rate_hz) - (time.time() - last_packet_sent_time)
            if wait_time > 0:
                time.sleep(wait_time)
            if crsf_frame == None or ser == None:
                continue
            throttle_value = int((throtle_curve(controller.get_combined_throttle())*810*controller.get_combined_throttle()*controller.get_combined_throttle()) + 992)
            steering_value = int((steering_curve(controller.get_steering())*810) + 992)
            last_throttle = throttle_value
            last_steering = steering_value
            frame = crsf_build_frame(
                PacketsTypes.RC_CHANNELS_PACKED,
                {"channels": [992, 992, 992, 992, 992, 992, 992, 992, 992, 992, 992, 992, 992, 992, steering_value, throttle_value]},)
            frame_size = len(frame)
            ser.write(frame)
            last_sent_frame = frame
            measured_packet_rate = 1/(time.time() - last_packet_sent_time)
            last_packet_sent_time = time.time()
        
            
    
if __name__ == '__main__':
    main()