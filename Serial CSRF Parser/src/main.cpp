#include <Arduino.h>
#include "crsf.h"

#define SYNC_BYTE 0xC8

#define RXD2 16
#define TXD2 17
#define SBUS_BUFFER_SIZE 25
uint8_t _rcs_buf[25]{};
uint16_t _raw_rc_values[RC_INPUT_MAX_CHANNELS]{};
uint16_t _raw_rc_count{};

int throttlePin = 25;
int rudderPin = 26;

int throttlePWMChannel = 3;
int rudderPWMChannel = 4;

void setServoUs(int us, int pwmChannel)
{
  const int full_duty_us = 20000;
  uint32_t duty = map(us, 0, full_duty_us, 0, 65536);
  ledcWrite(pwmChannel, duty);
}

void setup()
{
  // Note the format for setting a serial port is as follows: Serial2.begin(baud-rate, protocol, RX pin, TX pin);
  Serial.begin(460800);
  Serial2.begin(420000, SERIAL_8N1, RXD2, TXD2);

  ledcSetup(throttlePWMChannel, 50, 16);
  ledcSetup(rudderPWMChannel, 50, 16);
  setServoUs(1500, throttlePWMChannel);
  setServoUs(1500, rudderPWMChannel);
  ledcAttachPin(throttlePin, throttlePWMChannel);
  ledcAttachPin(rudderPin, rudderPWMChannel);
}

static uint16_t* parse_csrf_channels()
{
  static uint16_t channels[RC_INPUT_MAX_CHANNELS];
  static uint8_t buffer[25]{};
  
  while (Serial2.read() != SYNC_BYTE)
  {
  }
  // Read the next 25 bytes
  Serial2.readBytes(buffer, 25);

  if (buffer[0] != 0x18)
  {
    return channels;
  }

  // Parse the channels
  String hexString = "";
  for (int i = 0; i < 25; i++)
  {
    hexString += String(buffer[i], HEX) + " ";
  }
  Serial.println(hexString);
  
  for (int i = 0; i < 16; i++)
  {
    channels[i] = 1500;
  }
  return channels;
}

void loop()
{ // Choose Serial1 or Serial2 as required
  static uint32_t last_rcs_read_time = 0;
  static u_int32_t last_no_signal_time = 0;
  while (Serial2.available())
  {
    size_t numBytesRead = Serial2.readBytes(_rcs_buf, SBUS_BUFFER_SIZE);
    if (numBytesRead > 0)
    {
      //crsf_parse(&_rcs_buf[0], SBUS_BUFFER_SIZE, &_raw_rc_values[0], &_raw_rc_count, RC_INPUT_MAX_CHANNELS);

      memcpy(_raw_rc_values, parse_csrf_channels(), sizeof(_raw_rc_values));

      // wait for 100ms before starting to set the servos after the first signal is received
      if (last_no_signal_time - millis() > 500)
      {
        // Serial.println("");
        // Serial.print("Channel 1: ");
        // Serial.print(_raw_rc_values[0]);
        // Serial.print("\tChannel 2: ");
        // Serial.print(_raw_rc_values[1]);
        // Serial.print("\tChannel 3: ");
        // Serial.print(_raw_rc_values[2]);  
        // Serial.print("\tChannel 4: ");
        // Serial.print(_raw_rc_values[3]);
        // Serial.print("\tChannel 5: ");
        // Serial.print(_raw_rc_values[4]);
        // Serial.print("\tChannel 6: ");
        // Serial.print(_raw_rc_values[5]);
        // Serial.print("\tChannel 7: ");
        // Serial.print(_raw_rc_values[6]);
        // Serial.print("\tChannel 8: ");
        // Serial.print(_raw_rc_values[7]);      


        setServoUs(_raw_rc_values[0], throttlePWMChannel);
        setServoUs(_raw_rc_values[1], rudderPWMChannel);
      }
    }
    last_rcs_read_time = millis();
  }

  if (millis() - last_rcs_read_time > 50)
  {
    setServoUs(1500, throttlePWMChannel);
    setServoUs(1500, rudderPWMChannel);
    Serial.println("No signal");
    last_no_signal_time = millis();
  }
}