import network
import socket

# Setup Access Point
ssid = "Kanza's ESP"
password = "12345678"
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

print("Access Point Active, IP:", ap.ifconfig()[0])

# Start Web Server
def web_page():
    html = """<!DOCTYPE html>
    <html>
    <head><title>IoT-AI6thSp25 ESP32 Web Server</title></head>
    <body>
    <h1>ESP32 Web Server</h1>
    <p>Welcome to ESP32 Web Server in AP Mode for the IoT class of AI6th in SP25!</p>
    </body>
    </html>"""
    return html

# Setup Socket Server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 80))
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