# LED68 test sample
# looks like power-off sequence or something
# (C)2022-2023 @kani7

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
import random

bus = smbus.SMBus(1) # Using I2C Channel 1 (Pins 2 & 3)
LED68D1 = LED68.LED68(0x6f, bus, 0x3f)

LED68D1.enable()       # Required to start up the board
LED68D1.resetDriver()  # fresh start

LED68D1.setGroupBlink(0x01,0x20) # 12Hz, duty 32/256

LED68D1.setColor(1, 255, 0, 0)   # Red
LED68D1.setColor(2, 255, 0, 0)
LED68D1.setColor(3, 180, 45, 5)  # Yellow
LED68D1.setColor(4, 255, 0, 0)   # HD Red
LED68D1.LEDOn(1)
LED68D1.LEDOn(2)
sleep(4)
while(True):
# POWERON
  LED68D1.setColor(1, 120, 135, 0) # Yellow Green
  LED68D1.setColor(2, 0, 255, 0)   # Green
  sleep(3)
# HDD access
  for i in range(0,4):
    LED68D1.LEDOn(4)
    sleep(random.uniform(0.01, 0.9))
    LED68D1.LEDOff(4)
    sleep(random.uniform(0.03, 1.0))
  sleep(4)
# POWEROFF sequence
  for i in range(0,3):
    LED68D1.LEDOff(1)
    LED68D1.LEDOff(2)
    sleep(0.5)
    LED68D1.LEDOn(1)
    LED68D1.LEDOn(2)
    sleep(0.5)
  LED68D1.LEDOn(3)
  for i in range(0,3):
    LED68D1.LEDGroup(1)
    LED68D1.LEDGroup(2)
    sleep(0.5)
    LED68D1.LEDOn(1)
    LED68D1.LEDOn(2)
    sleep(0.5)
  LED68D1.setColor(1, 255, 0, 0) # Red
  LED68D1.setColor(2, 255, 0, 0)
  LED68D1.LEDOff(3)
  sleep(4)
