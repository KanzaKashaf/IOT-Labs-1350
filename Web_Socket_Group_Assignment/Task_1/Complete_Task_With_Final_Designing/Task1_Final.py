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

def update_oled(message):
    oled.fill(0)
    oled.text(message, 0, 0)
    oled.show()
    
# Function to decode URL-encoded strings
def decode_url_encoded_string(s):
    result = ""
    i = 0
    while i < len(s):
        if s[i] == "%":
            # Decode URL-encoded characters (e.g., %20 -> space)
            hex_value = s[i+1:i+3]
            result += chr(int(hex_value, 16))
            i += 3
        elif s[i] == "+":
            # Replace '+' with space
            result += " "
            i += 1
        else:
            result += s[i]
            i += 1
    return result    

def web_page():
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ESP32 OLED Display</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #ffffff;
            margin: 0;
            padding: 20px;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: auto;
            position: relative;
            transition: background 1s ease;
        }

        /* Default Spring Background */
        body.spring {
            background: linear-gradient(135deg, #87CEEB, #1E90FF); /* Sky blue */
        }

        /* Summer Background (High Temperature) */
        body.summer {
            background: linear-gradient(135deg, #FFA500, #FF4500); /* Orange */
        }

        /* Winter Background (Low Temperature) */
        body.winter {
            background: linear-gradient(135deg, #2F4F4F, #1E1E2F); /* Dark gray */
        }

        /* Background Graphics */
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
            width: 80px;
            height: 80px;
            top: -40px;
            left: 20px;
        }
        .cloud::after {
            width: 60px;
            height: 60px;
            top: -30px;
            right: 20px;
        }
        .cloud.one {
            width: 150px;
            height: 50px;
            top: 10%;
            left: -200px;
            animation-duration: 25s;
        }
        .cloud.two {
            width: 200px;
            height: 70px;
            top: 30%;
            right: -200px;
            animation-duration: 30s;
        }
        .cloud.three {
            width: 180px;
            height: 60px;
            top: 50%;
            left: -200px;
            animation-duration: 35s;
        }

        .sun {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 80px;
            height: 80px;
            background: #FFD700;
            border-radius: 50%;
            box-shadow: 0 0 50px #FFD700;
            animation: glow 2s infinite alternate;
            z-index: 2;
        }

        .storm {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1;
            display: none;
        }

        @keyframes moveClouds {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100vw); }
        }

        @keyframes glow {
            0% { box-shadow: 0 0 50px #FFD700; }
            100% { box-shadow: 0 0 70px #FFD700; }
        }

        h1 {
            color: #ff6f61;
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            z-index: 3;
        }
        h2 {
            color: #a8e6cf;
            font-size: 1.8em;
            margin: 10px 0;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
            z-index: 3;
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
            transition: background-color 0.3s ease, transform 0.2s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            z-index: 3;
        }
        button:hover {
            background-color: #ff3b2f;
            transform: translateY(-2px);
        }
        .input_rgb, .sensor-data, form {
            z-index: 3;
        }

        /* Enhanced Button Styles */
        .input_rgb input[type="submit"], form input[type="submit"] {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 15px 30px;
            margin: 10px;
            cursor: pointer;
            border-radius: 25px;
            font-size: 1.2em;
            transition: background 0.3s ease, transform 0.2s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        .input_rgb input[type="submit"]:hover, form input[type="submit"]:hover {
            background: linear-gradient(135deg, #45a049, #4CAF50);
            transform: translateY(-2px);
        }

        .input_rgb input[type="number"] {
            padding: 10px;
            width: 80px;
            border-radius: 25px;
            border: 2px solid #4CAF50;
            background-color: rgba(46, 46, 74, 0.8);
            color: #ffffff;
            font-size: 1.1em;
            margin-right: 10px;
            transition: border-color 0.3s ease;
        }
        .input_rgb input[type="number"]:focus {
            border-color: #ff6f61;
        }

        form input[type="text"] {
            padding: 10px;
            width: 250px;
            border-radius: 25px;
            border: 2px solid #4CAF50;
            background-color: rgba(46, 46, 74, 0.8);
            color: #ffffff;
            font-size: 1.1em;
            transition: border-color 0.3s ease;
        }
        form input[type="text"]:focus {
            border-color: #ff6f61;
        }
    </style>
    <script>
        function updateSensorData() {
            fetch('/sensor')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('temp').innerText = data.temp + " °C 🌡";
                    document.getElementById('humidity').innerText = data.humidity + " % 💧";

                    // Change background based on temperature
                    const body = document.body;
                    const storm = document.querySelector('.storm');
                    if (data.temp > 27) {
                        body.className = 'summer';
                        storm.style.display = 'none';
                    } else if (data.temp < 25) {
                        body.className = 'winter';
                        storm.style.display = 'block';
                    } else {
                        body.className = 'spring';
                        storm.style.display = 'none';
                    }
                })
                .catch(error => console.error('Error fetching sensor data:', error));
        }

        function sendText() {
            const text = document.getElementById('textInput').value;
            fetch('/display', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            })
            .then(response => response.text())
            .then(data => console.log(data))
            .catch(error => console.error('Error sending text:', error));
        }

        // Update sensor data every 2 seconds
        setInterval(updateSensorData, 2000);
    </script>
</head>
<body class="spring">
    <!-- Background Graphics -->
    <div class="cloud one"></div>
    <div class="cloud two"></div>
    <div class="cloud three"></div>
    <div class="sun"></div>
    <div class="storm"></div>

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
    <br>
    <div class="sensor-data">
        <h1>🌡 TEMPERATURE AND HUMIDITY 💧</h1>
        <h2>Temp: <span id="temp">...</span></h2>
        <h2>Humidity: <span id="humidity">...</span></h2>
    </div>
    <br>
    <h1>📺 OLED Display</h1>
    <form action="/">
        <input name="msg" id="textInput" type="text" placeholder="Enter text to display...">
        <input type="submit" value="Send ✔">
    </form>
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
    elif "?R=" in request and "&G=" in request and "&B=" in request:
        try:
            r = int(request.split("R=")[1].split("&")[0])
            g = int(request.split("G=")[1].split("&")[0])
            b = int(request.split("B=")[1].split(" ")[0])
            neo[0] = (r, g, b)
            neo.write()
        except:
            pass
    elif "msg=" in request:
        try:
            # Extract the query string from the request
            parts = request.split(" ")
            if len(parts) > 1:
                path_and_query = parts[1]
                query_parts = path_and_query.split("?")
                if len(query_parts) > 1:
                    query_string = query_parts[1]
                    # Extract the "msg" parameter
                    msg_parts = query_string.split("msg=")
                    if len(msg_parts) > 1:
                        msg = msg_parts[1].split("&")[0]  # Get the value of "msg"
                        msg = decode_url_encoded_string(msg)  # Decode URL-encoded characters
                        update_oled(msg)
        except Exception as e:
            print("Error parsing request:", e)
    
        
    
    if request.startswith("GET /sensor "):
        # Handle sensor data request
        temp, humidity = read_dht_sensor()
        if temp is None or humidity is None:
            temp = "..."
            humidity = "..."
        sensor_data = {"temp": temp, "humidity": humidity}
        conn.send("HTTP/1.1 200 OK\nContent-Type: application/json\n\n")
        conn.send(json.dumps(sensor_data))
    else:
        # Serve the main webpage
        response = web_page()
        conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
        conn.send(response)
    
    conn.close()
