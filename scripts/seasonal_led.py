# LED68 seasonal illumination sample
# (C)2021-2025 @kani7

#    Wiring
# RPi     LED Driver
# ---     ----------
# 3.3v ->    VCC
# GND  ->    GND
#  2   ->    SDA
#  3   ->    SCL
#

import LED68
import smbus
from time import sleep
import math

I2C_ADDR = 0x6f
LED_MAP = [1, 2, 3, 4]
#LED_MAP = [1, 3, 4]

# settings for December
PHASE = 2.3
SPEED = 0.1
HUE_BASE = 0.33
HUE_SWEEP = 0.13
VAL_BASE = 0.6
VAL_SWEEP = 0.3
VISUAL_R = 1.0
VISUAL_G = 0.4
VISUAL_B = 1.1

def hsv2rgb(h, s, v):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r*255), int(g*255), int(b*255)

def derating(r, g, b):
    return (
        min(int(r * VISUAL_R / 3), 255),
        min(int(g * VISUAL_G / 3), 255),
        min(int(b * VISUAL_B / 3), 255)
    )

bus = smbus.SMBus(1)    # Using I2C Channel 1 (Pins 2 & 3)
LED68D1 = LED68.LED68(I2C_ADDR, bus, 0x3f)
LED68D1.enable()        # Required to start up the board
LED68D1.resetDriver()   # fresh start

for i in LED_MAP:
    LED68D1.LEDOn(i)

TWO_PI = 2 * math.pi
t = 0.0
while(True):
    for i, led in enumerate(LED_MAP):
        hue = (HUE_BASE + HUE_SWEEP * math.sin(t + i * PHASE)) % 1.0
        val = VAL_BASE + VAL_SWEEP * math.sin(t + i)
        rgb = hsv2rgb(hue, 1.0, max(0.0, val))
        rgb = derating(*rgb)
        LED68D1.setColor(led, *rgb)
    sleep(SPEED)
    t += SPEED
    if t > TWO_PI:
        t -= TWO_PI
