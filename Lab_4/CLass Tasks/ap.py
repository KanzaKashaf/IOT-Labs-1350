import network

ssid = "Kanza's ESP"
password = "12345678"  # Minimum 8 characters
auth_mode = network.AUTH_WPA2_PSK  # Secure mode (recommended)

# Create an Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)  # Activate AP mode
ap.config(essid=ssid, password=password, authmode=auth_mode)  # Set SSID and password

print("Access Point Active")
print("AP IP Address:", ap.ifconfig()[0])



# security modes

# network.AUTH_OPEN	        0	No password, open network (not secure)
# network.AUTH_WEP	        1	WEP security (not recommended due to weak security)
# network.AUTH_WPA_PSK	    2	WPA-PSK security (commonly used, secure)
# network.AUTH_WPA2_PSK	    3	WPA2-PSK security (stronger security, recommended)
# network.AUTH_WPA_WPA2_PSK	4	WPA/WPA2 mixed mode