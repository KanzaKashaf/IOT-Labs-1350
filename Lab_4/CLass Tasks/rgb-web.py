import network
import socket
import time
from machine import Pin
from neopixel import NeoPixel

pin = Pin(48, Pin.OUT)   # set GPIO48  to output to drive NeoPixel
neo = NeoPixel(pin, 1)   # create NeoPixel driver on GPIO48 for 1 pixel

# Connect to Wi-Fi
ssid = "K.K"
password = "101213456"
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid, password)

while not sta.isconnected():
    time.sleep(1)

print("Connected! IP:", sta.ifconfig()[0])

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
s.bind((sta.ifconfig()[0], 80))
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