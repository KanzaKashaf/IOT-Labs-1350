print("Hello, ESP32-S3!")



import network
from machine import Pin

# Initialize the Wi-Fi interface in Station mode and activate it
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

# Perform the Wi-Fi scan
print("Scanning Wi-Fi... ", end="")
nets = wifi.scan()
print(f"{len(nets)} network(s)")

print(nets[0])

for net in nets:
    ssid = net[0].decode("utf-8")
    print(f" \t{ssid}")

# Print the list of available Wi-Fi networks
# print("RSSI Channel \tSSID")
# for net in nets:
#     rssi = net[3]
#     channel = net[2]
#     ssid = net[0].decode("utf-8")
#     print(f"{rssi}  (ch.{channel}) \t{ssid}")