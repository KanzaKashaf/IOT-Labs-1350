# main.py -- put your code here!

from machine import Pin
from neopixel import NeoPixel
import time

pin = Pin(48, Pin.OUT)   # Set GPIO48 to output to drive NeoPixel
neo = NeoPixel(pin, 1)   # Create NeoPixel driver on GPIO48 for 1 pixel

while True:
    neo[0] = (0, 255, 0)  # Set the pixel to green
    neo.write()           # Write data to the pixel
    time.sleep(1)       # Wait for 0.5 seconds
    
    neo[0] = (255, 0, 0)  # Set the pixel to red
    neo.write()
    time.sleep(1)       # Wait for 0.5 seconds

    neo[0] = (0, 0, 255)  # Set the pixel to red
    neo.write()
    time.sleep(1)