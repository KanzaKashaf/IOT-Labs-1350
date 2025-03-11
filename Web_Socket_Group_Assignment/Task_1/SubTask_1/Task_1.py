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
    <head><meta charset="UTF-8">
        <title>ESP32 OLED Display</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #1e1e2f;
                color: #ffffff;
                margin: 0;
                padding: 20px;
                text-align: center;
            }
            h1 {
                color: #ff6f61;
                font-size: 2.5em;
                margin-bottom: 20px;
            }
            h2 {
                color: #a8e6cf;
                font-size: 1.8em;
                margin: 10px 0;
            }
            button {
                background-color: #ff6f61;
                color: white;
                border: none;
                padding: 15px 30px;
                margin: 10px;
                cursor: pointer;
                border-radius: 25px;
                font-size: 1.2em;
                transition: background-color 0.3s ease;
            }
            button:hover {
                background-color: #ff3b2f;
            }
            .rgb-buttons {
                margin-top: 20px;
            }
            .rgb-buttons button {
                background-color: #4CAF50;
            }
            .rgb-buttons button:nth-child(1) {
                background-color: #ff6f61;
            }
            .rgb-buttons button:nth-child(2) {
                background-color: #4CAF50;
            }
            .rgb-buttons button:nth-child(3) {
                background-color: #008CBA;
            }
            .input_rgb {
                background-color: #2e2e4a;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
                display: inline-block;
                margin-top: 20px;
            }
            .input_rgb label {
                font-size: 1.2em;
                margin-right: 10px;
            }
            .input_rgb input[type="number"] {
                padding: 10px;
                width: 80px;
                border-radius: 25px;
                border: 2px solid #4CAF50;
                background-color: #2e2e4a;
                color: #ffffff;
                font-size: 1.1em;
                margin-right: 10px;
            }
            .input_rgb input[type="submit"] {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1.1em;
                transition: background-color 0.3s ease;
            }
            .input_rgb input[type="submit"]:hover {
                background-color: #45a049;
            }
            form {
                margin-top: 20px;
            }
        </style>
    <body>
    <h1>ESP32 OLED Display</h1>
        <div class="rgb-buttons">
            <a href="/?RGB=red"><button>🔴 Turn RGB RED</button></a>
            <a href="/?RGB=green"><button>🟢 Turn RGB GREEN</button></a>
            <a href="/?RGB=blue"><button>🔵 Turn RGB BLUE</button></a>
        </div>
        <div class="input_rgb">
            <h2>RGB LED Control</h2>
            <form action="/" method="GET">
                <label>R:</label> <input type="number" name="R" min="0" max="255" value="0">
                <label>G:</label> <input type="number" name="G" min="0" max="255" value="0">
                <label>B:</label> <input type="number" name="B" min="0" max="255" value="0">
                <input type="submit" value="Set Color">
            </form>
        </div>
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
        neo[0] = (255, 0, 0)  # set the first pixel to red
        neo.write()            # write data to all pixels
    elif "/?RGB=green" in request:
        neo[0] = (0, 255, 0)  # set the first pixel to green
        neo.write()            # write data to all pixels
    elif "/?RGB=blue" in request:
        neo[0] = (0, 0, 255)  # set the first pixel to blue
        neo.write()            # write data to all pixels
    elif "?R=" in request and "&G=" in request and "&B=" in request:
        try:
            r = int(request.split("R=")[1].split("&")[0])
            g = int(request.split("G=")[1].split("&")[0])
            b = int(request.split("B=")[1].split(" ")[0])
            neo[0] = (r, g, b)
            neo.write()
        except:
            pass
        
    response = web_page()
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
    conn.send(response)
    conn.close()