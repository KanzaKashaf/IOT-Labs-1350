import network
import socket
import time

# Connect to Wi-Fi
ssid = "okokok"
password = "09000000"
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
    <head><title>ESP32 Web Server as station mode</title></head>
    <body>
    <h1>ESP32 Web Server station mode</h1>
    <p>Welcome! Your ESP32 is connected to Wi-Fi IoT for AI6th.</p>
    </body>
    </html>"""
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((sta.ifconfig()[0], 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print("Connection from:", addr)
    request = conn.recv(1024)
    print("Request:", request)
    
    response = web_page()
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
    conn.send(response)
    conn.close()