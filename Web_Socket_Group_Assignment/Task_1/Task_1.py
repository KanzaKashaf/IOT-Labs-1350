print("Hello, ESP32-S3!")

import network
import time
import socket
from machine import Pin
from neopixel import NeoPixel 

pin = Pin(48, Pin.OUT)   # set GPIO48  to output to drive NeoPixel
neo = NeoPixel(pin, 1)   # create NeoPixel driver on GPIO48 for 1 pixel

ssid_st = "K.K"
password_st = "101213456"

print("Connecting to WiFi", end="")
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid_st , password_st)

# Wait for connection
for _ in range(10):
    if sta.isconnected():
        break
    time.sleep(1)
    
    
if sta.isconnected():
    print("Connected to WiFi!")
    print("IP Address as station:", sta.ifconfig()[0])
else:
    print("Failed to connect")
    

ssid_ap = "Kanza's ESP32_AP"
password_ap = "12345678"  # Minimum 8 characters
auth_mode = network.AUTH_WPA2_PSK  # Secure mode (recommended)

# Create an Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)  # Activate AP mode
ap.config(essid=ssid_ap, password=password_ap, authmode=auth_mode)  # Set SSID and password

print("Access Point Active")
print("AP IP Address:", ap.ifconfig()[0])


# Start Web Server
def web_page():
    
    html = """<!DOCTYPE html>
    <html>
    <head><title>ESP32 RGB LED Control</title></head>
    <body>
    <h1>ESP32 RGB led Control</h1>
    <p><a href="/?RGB=red"><button>Turn RGB RED</button></a></p>
    <p><a href="/?RGB=green"><button>Turn RGB GREEN</button></a></p>
    <p><a href="/?RGB=blue"><button>Turn RGB BLUE</button></a></p>
    </body>
    </html>"""
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print("Connection from:", addr)
    request = conn.recv(1024).decode()
    print("Request:", request)
    
    if "/?RGB=red" in request:
        neo[0] = (255, 0, 0) # set the first pixel to red
        neo.write()              # write data to all pixels
    elif "/?RGB=green" in request:
        neo[0] = (0, 255, 0) # set the first pixel to green
        neo.write()              # write data to all pixels
    elif "/?RGB=blue" in request:
        neo[0] = (0, 0, 255) # set the first pixel to blue
        neo.write()              # write data to all pixels
        
    response = web_page()
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
    conn.send(response)
    conn.close()