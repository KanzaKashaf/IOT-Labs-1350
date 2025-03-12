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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobile Weather App</title>
    <style>
        /* General Styles */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
            position: relative;
            background: linear-gradient(135deg, #1e1e2f, #2e2e4a);
        }

        /* Blurred Web Background */
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #1e1e2f, #2e2e4a); /* Same as mobile frame */
            filter: blur(5px); /* Slight blur */
            z-index: -1;
        }

        /* Mobile Frame */
        .mobile-frame {
            width: 90%;
            max-width: 300px;
            height: 500px; /* Reduced height to fit without scrolling */
            background: #1e1e2f;
            border-radius: 30px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
            border: 2px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
            position: relative;
            margin: 20px;
        }

        /* Backgrounds */
        .background {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            transition: opacity 1s ease;
        }

        .day-sky {
            background: linear-gradient(135deg, #87CEEB, #1E90FF);
        }

        .hot-sky {
            background: linear-gradient(135deg, #FFA500, #FF4500);
        }

        .night-sky {
            background: linear-gradient(135deg, #2F4F4F, #1E1E2F);
        }

        /* Graphics */
        .cloud {
            position: absolute;
            background: white;
            border-radius: 1000px;
            animation: moveClouds 20s linear infinite;
        }
        .cloud::before, .cloud::after {
            content: '';
            position: absolute;
            background: white;
            border-radius: 1000px;
        }
        .cloud::before {
            width: 60px;
            height: 60px;
            top: -30px;
            left: 10px;
        }
        .cloud::after {
            width: 40px;
            height: 40px;
            top: -20px;
            right: 10px;
        }
        .cloud.one {
            width: 120px;
            height: 40px;
            top: 20%;
            left: -150px;
            animation-duration: 25s;
        }
        .cloud.two {
            width: 150px;
            height: 50px;
            top: 40%;
            right: -150px;
            animation-duration: 30s;
        }

        .sun {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: #FFD700;
            border-radius: 50%;
            box-shadow: 0 0 30px #FFD700;
            animation: glow 2s infinite alternate;
        }

        .moon {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: #F0F0F0;
            border-radius: 50%;
            box-shadow: 0 0 30px #F0F0F0;
        }

        .star {
            position: absolute;
            background: white;
            width: 2px;
            height: 2px;
            border-radius: 50%;
            box-shadow: 0 0 5px white;
            animation: twinkle 2s infinite alternate;
        }

        @keyframes moveClouds {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        @keyframes glow {
            0% { box-shadow: 0 0 30px #FFD700; }
            100% { box-shadow: 0 0 50px #FFD700; }
        }

        @keyframes twinkle {
            0% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        /* Content */
        .content {
            position: relative;
            z-index: 2;
            text-align: center;
            color: white;
            padding: 60px 20px 20px; /* Adjusted padding-top to move text down */
        }

        h1 {
            font-size: 1.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* Added shadow */
        }

        h2 {
            font-size: 1.2em;
            margin: 5px 0;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5); /* Added shadow */
        }

        /* Alert Messages */
        .alert {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.9);
            color: #1e1e2f;
            padding: 10px 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
            animation: slideUp 0.5s ease;
            z-index: 3;
        }

        @keyframes slideUp {
            0% { transform: translate(-50%, 100%); }
            100% { transform: translate(-50%, 0); }
        }
    </style>
</head>
<body>
    <div class="mobile-frame">
        <!-- Backgrounds -->
        <div class="background day-sky"></div>
        <div class="background hot-sky" style="opacity: 0;"></div>
        <div class="background night-sky" style="opacity: 0;"></div>

        <!-- Graphics -->
        <div class="cloud one"></div>
        <div class="cloud two"></div>
        <div class="sun"></div>
        <div class="moon" style="opacity: 0;"></div>
        <div class="star" style="top: 10%; left: 20%;"></div>
        <div class="star" style="top: 30%; left: 50%;"></div>
        <div class="star" style="top: 50%; left: 70%;"></div>

        <!-- Content -->
        <div class="content">
            <h1>Weather Station</h1>
            <h2>🌡 Temperature: <span id="temp">...</span></h2>
            <h2>💧 Humidity: <span id="humidity">...</span></h2>
        </div>

        <!-- Alert Messages -->
        <div id="alert" class="alert" style="display: none;">Alert Message</div>
    </div>

    <script>
        // Function to fetch sensor data and update the UI
        function updateSensorData() {
            fetch('/sensor') // Replace with your sensor data endpoint
                .then(response => response.json())
                .then(data => {
                    const tempElement = document.getElementById('temp');
                    const humidityElement = document.getElementById('humidity');
                    const daySky = document.querySelector('.day-sky');
                    const hotSky = document.querySelector('.hot-sky');
                    const nightSky = document.querySelector('.night-sky');
                    const sun = document.querySelector('.sun');
                    const moon = document.querySelector('.moon');
                    const alertElement = document.getElementById('alert');

                    // Update Temperature and Humidity
                    tempElement.innerText = ${data.temp}°C;
                    humidityElement.innerText = ${data.humidity}%;

                    // Change Background and Graphics based on Temperature
                    if (data.temp === 25) {
                        daySky.style.opacity = 1;
                        hotSky.style.opacity = 0;
                        nightSky.style.opacity = 0;
                        sun.style.opacity = 1;
                        moon.style.opacity = 0;
                        alertElement.innerText = "🌤 Normal Temperature!";
                    } else if (data.temp > 26) {
                        daySky.style.opacity = 0;
                        hotSky.style.opacity = 1;
                        nightSky.style.opacity = 0;
                        sun.style.opacity = 1;
                        moon.style.opacity = 0;
                        alertElement.innerText = "🔥 Hot Temperature!";
                    } else if (data.temp < 25) {
                        daySky.style.opacity = 0;
                        hotSky.style.opacity = 0;
                        nightSky.style.opacity = 1;
                        sun.style.opacity = 0;
                        moon.style.opacity = 1;
                        alertElement.innerText = "❄ Cold Temperature!";
                    }

                    // Show Alert
                    alertElement.style.display = 'block';
                    setTimeout(() => {
                        alertElement.style.display = 'none';
                    }, 3000);
                })
                .catch(error => console.error('Error fetching sensor data:', error));
        }

        // Fetch sensor data every 2 seconds
        setInterval(updateSensorData, 2000);

        // Initial fetch
        updateSensorData();
    </script>
</body>
</html>"""
    return html

# Start web server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0",80))
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