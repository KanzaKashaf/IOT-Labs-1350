import network
import time
import socket
from machine import Pin
from neopixel import NeoPixel
import dht
import json  # For JSON responses

# DHT Sensor setup
dht_pin = 4
dht_sensor = dht.DHT11(Pin(dht_pin))

# NeoPixel setup
pin = Pin(48, Pin.OUT)
neo = NeoPixel(pin, 1)

# WiFi credentials
ssid_st = "K.K"
password_st = "101213456"

# Connect to WiFi
print("Connecting to WiFi", end="")
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid_st, password_st)

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

# Access Point setup
ssid_ap = "Kanza's ESP32_AP"
password_ap = "12345678"
auth_mode = network.AUTH_WPA2_PSK

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid_ap, password=password_ap, authmode=auth_mode)

print("Access Point Active")
print("AP IP Address:", ap.ifconfig()[0])

# Function to read DHT sensor with error handling
def read_dht_sensor():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temp, humidity
    except Exception as e:
        print("Failed to read DHT sensor:", e)
        return None, None

# Web server function
def web_page():
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 RGB LED Control</title>
        <script>
            function updateSensorData() {
                fetch('/sensor')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('temp').innerText = data.temp;
                        document.getElementById('humidity').innerText = data.humidity;
                    })
                    .catch(error => console.error('Error fetching sensor data:', error));
            }

            // Update sensor data every 2 seconds
            setInterval(updateSensorData, 2000);
        </script>
    </head>
    <body>
        <h1>ESP32 RGB LED Control</h1>
        <p><a href="/?RGB=red"><button>Turn RGB RED</button></a></p>
        <p><a href="/?RGB=green"><button>Turn RGB GREEN</button></a></p>
        <p><a href="/?RGB=blue"><button>Turn RGB BLUE</button></a></p>
        <br>
        <h1>TEMPERATURE AND HUMIDITY</h1>
        <h2>Temp: <span id="temp">N/A</span></h2>
        <h2>Humidity: <span id="humidity">N/A</span></h2>
    </body>
    </html>"""
    return html

# Start web server
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
    
    if request.startswith("GET /sensor "):
        # Handle sensor data request
        temp, humidity = read_dht_sensor()
        if temp is None or humidity is None:
            temp = "N/A"
            humidity = "N/A"
        sensor_data = {"temp": temp, "humidity": humidity}
        conn.send("HTTP/1.1 200 OK\nContent-Type: application/json\n\n")
        conn.send(json.dumps(sensor_data))
    else:
        # Serve the main webpage
        response = web_page()
        conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
        conn.send(response)
    
    conn.close()
