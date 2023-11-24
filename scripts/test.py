# LED68 test sample
# (C)2021-2023 @kani7

#    Wiring
# RPi     LED Driver
# ---     ----------
# 3.3v ->    VCC
# GND  ->    GND
#  2   ->    SDA
#  3   ->    SCL
#

import LED68
from time import sleep
import smbus

bus = smbus.SMBus(1)    # Using I2C Channel 1 (Pins 2 & 3)
LED68D1 = LED68.LED68(0x6f, bus, 0x3f)

LED68D1.enable()        # Required to start up the board
LED68D1.resetDriver()   # fresh start

LED68D1.LEDOn(1)
LED68D1.LEDOn(2)
LED68D1.LEDOn(3)
LED68D1.LEDOn(4)

while(True):
  for i in range(1,255):
    LED68D1.setColor(1, i, 0, 0)
    LED68D1.setColor(2, i, 0, 0)
    LED68D1.setColor(3, i, 0, 0)
    LED68D1.setColor(4, i, 0, 0)
    sleep(0.01)
  sleep(0.7)
  for i in range(1,255):
    LED68D1.setColor(1, 0, i, 0)
    LED68D1.setColor(2, 0, i, 0)
    LED68D1.setColor(3, 0, i, 0)
    LED68D1.setColor(4, 0, i, 0)
    sleep(0.01)
  sleep(0.7)
  for i in range(1,255):
    LED68D1.setColor(1, 0, 0, i)
    LED68D1.setColor(2, 0, 0, i)
    LED68D1.setColor(3, 0, 0, i)
    LED68D1.setColor(4, 0, 0, i)
    sleep(0.01)
  sleep(0.7)
