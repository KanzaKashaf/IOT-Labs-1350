import network
import time
import socket
from machine import Pin, I2C
from neopixel import NeoPixel
import dht
import json
from ssd1306 import SSD1306_I2C  # OLED display library

# DHT Sensor setup
dht_pin = 4
dht_sensor = dht.DHT11(Pin(dht_pin))

# NeoPixel setup
pin = Pin(48, Pin.OUT)
neo = NeoPixel(pin, 1)

# OLED Display setup
i2c = I2C(0, scl=Pin(9), sda=Pin(8))  # Use GPIO9 for SCL and GPIO8 for SDA
oled = SSD1306_I2C(128, 64, i2c)  # Change to 128x32 if using a smaller display
print("OLED initialized")

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

# Variables to store previous sensor values
prev_temp = None
prev_humidity = None

# Function to read DHT sensor with error handling
def read_dht_sensor():
    global prev_temp, prev_humidity
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        prev_temp = temp
        prev_humidity = humidity
        return temp, humidity
    except Exception as e:
        print("Failed to read DHT sensor:", e)
        return prev_temp, prev_humidity  # Return previous values if sensor fails

# Function to update OLED display
def update_oled(temp, humidity, temp_alert, humidity_alert):
    oled.fill(0)
    oled.text("Temp: {} C".format(temp), 0, 0)
    oled.text("Humidity: {} %".format(humidity), 0, 16)
    oled.text("{}".format(temp_alert), 0, 32)
    oled.text("{}".format(humidity_alert), 0, 48)
    oled.show()

# Function to blink NeoPixel LED
def blink_led(color, blink_count=5, delay=0.5):
    for _ in range(blink_count):
        neo[0] = color
        neo.write()
        time.sleep(delay)
        neo[0] = (0, 0, 0)
        neo.write()
        time.sleep(delay)

# HTML page with JavaScript for polling
def web_page():
    html = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ESP32 Weather Station</title>
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
            .sensor-data {
                background-color: #2e2e4a;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
                display: inline-block;
                margin-top: 20px;
            }
            .emoji {
                font-size: 1.5em;
            }
            .alert {
                font-size: 1.2em;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .alert.temp-low {
                background-color: #008CBA; /* Blue */
            }
            .alert.temp-normal {
                background-color: #FFD700; /* Yellow */
            }
            .alert.temp-high {
                background-color: #FF0000; /* Red */
                animation: blink 1s infinite;
            }
            .alert.humidity-dry {
                background-color: #FFA500; /* Orange */
            }
            .alert.humidity-normal {
                background-color: #4CAF50; /* Green */
            }
            .alert.humidity-high {
                background-color: #800080; /* Purple */
            }
            @keyframes blink {
                0% { opacity: 1; }
                50% { opacity: 0; }
                100% { opacity: 1; }
            }
        </style>
        <script>
            function updateSensorData() {
                fetch('/sensor')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('temp').innerText = data.temp + " °C 🌡";
                        document.getElementById('humidity').innerText = data.humidity + " % 💧";

                        // Temperature Alerts
                        var tempAlertDiv = document.getElementById('temp-alert');
                        if (data.temp < 25) {
                            tempAlertDiv.innerHTML = '<div class="alert temp-low">🌡 Low Temperature! ❄</div>';
                            fetch('/rgb?color=blue');
                        } else if (data.temp >= 25 && data.temp <= 26) {
                            tempAlertDiv.innerHTML = '<div class="alert temp-normal">🌡 Normal Temperature! 😊</div>';
                            fetch('/rgb?color=yellow');
                        } else if (data.temp >= 27) {
                            tempAlertDiv.innerHTML = '<div class="alert temp-high">🌡 High Temperature! 🔥</div>';
                            fetch('/rgb?color=red');
                        }

                        // Humidity Alerts
                        var humidityAlertDiv = document.getElementById('humidity-alert');
                        if (data.humidity < 50) {
                            humidityAlertDiv.innerHTML = '<div class="alert humidity-dry">💧 Dry! 🏜</div>';
                        } else if (data.humidity >= 50 && data.humidity < 70) {
                            humidityAlertDiv.innerHTML = '<div class="alert humidity-normal">💧 Normal Humidity! 😊</div>';
                        } else if (data.humidity >= 70) {
                            humidityAlertDiv.innerHTML = '<div class="alert humidity-high">💧 High Humidity! 💦</div>';
                        }
                    })
                    .catch(error => console.error('Error fetching sensor data:', error));
            }

            // Update sensor data every 2 seconds
            setInterval(updateSensorData, 2000);
        </script>
    </head>
    <body>
        <h1>ESP32 Weather Station</h1>
        <div class="sensor-data">
            <h1>🌡 TEMPERATURE AND HUMIDITY 💧</h1>
            <h2>Temp: <span id="temp">N/A</span></h2>
            <h2>Humidity: <span id="humidity">N/A</span></h2>
            <div id="temp-alert"></div>
            <div id="humidity-alert"></div>
        </div>
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

    if "/sensor" in request:
        # Handle sensor data request
        temp, humidity = read_dht_sensor()
        if temp is None or humidity is None:
            temp = prev_temp
            humidity = prev_humidity
        sensor_data = {"temp": temp, "humidity": humidity}
        conn.send("HTTP/1.1 200 OK\nContent-Type: application/json\n\n")
        conn.send(json.dumps(sensor_data))

        # Determine alerts
        temp_alert = ""
        humidity_alert = ""
        if temp < 25:
            temp_alert = "Low Temperature! ❄"
        elif 25 <= temp <= 26:
            temp_alert = "Normal Temperature! 😊"
        elif temp >= 27:
            temp_alert = "High Temperature! 🔥"
            blink_led((255, 0, 0))  # Blink red LED for high temperature

        if humidity < 50:
            humidity_alert = "Dry! 🏜"
        elif 50 <= humidity < 70:
            humidity_alert = "Normal Humidity! 😊"
        elif humidity >= 70:
            humidity_alert = "High Humidity! 💦"

        # Update OLED display
        update_oled(temp, humidity, temp_alert, humidity_alert)
    elif "/rgb?color=red" in request:
        neo[0] = (255, 0, 0)  # Set RGB to red
        neo.write()
        conn.send("HTTP/1.1 200 OK\n\n")
    elif "/rgb?color=blue" in request:
        neo[0] = (0, 0, 255)  # Set RGB to blue
        neo.write()
        conn.send("HTTP/1.1 200 OK\n\n")
    elif "/rgb?color=yellow" in request:
        neo[0] = (255, 255, 0)  # Set RGB to yellow
        neo.write()
        conn.send("HTTP/1.1 200 OK\n\n")
    else:
        # Serve the main webpage
        response = web_page()
        conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
        conn.send(response)

    conn.close()