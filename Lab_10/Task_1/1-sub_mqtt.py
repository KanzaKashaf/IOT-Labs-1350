import machine
import dht
import time
import ujson
from machine import Pin, SoftI2C
import ssd1306
from umqtt.simple import MQTTClient
import network

#wifi configuration

WIFI_SSID = 'NTU FSD'
WIFI_PASS = ''


print(f"Connecting to WiFi network '{WIFI_SSID}'")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

timeout = 10  # 10 seconds max wait 
while not wifi.isconnected() and timeout > 0:
    time.sleep(1)
    print('WiFi connect retry ...')
    timeout -= 1

# checking wifi onnected or not
if wifi.isconnected():
    print('WiFi Connected! IP:', wifi.ifconfig()[0])
else:
    print('Failed to connect to WiFi. Check credentials or network.')



# Configuration
THINGSPEAK_MQTT_HOST = "mqtt3.thingspeak.com"
THINGSPEAK_MQTT_PORT = 1883

THINGSPEAK_CHANNEL_ID = "2970621"
# got after creating mqtt device
THINGSPEAK_CLIENT_ID = "DTIJOw07IwM6ETwmPSAwJh4"
THINGSPEAK_USERNAME = "DTIJOw07IwM6ETwmPSAwJh4"
THINGSPEAK_MQTT_API_KEY = "tkkLiyXk0MzlEqbJi4yC6ESL"

DHT_PIN = 4
CHECK_INTERVAL = 20

# MQTT topic format: channels/<channel_id>/publish
MQTT_TOPIC = f"channels/{THINGSPEAK_CHANNEL_ID}/publish"

# Initialize hardware
dht_sensor = dht.DHT11(Pin(DHT_PIN))
i2c = SoftI2C(scl=Pin(9), sda=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
# reading sensor data
def read_sensor():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temp, humidity
    except Exception as e:
        print("Sensor read error:", e)
        return None, None
# to thingspeaak
def send_to_thingspeak_mqtt(client, temp, humidity):
    try:
        payload = f"field1={temp}&field2={humidity}"
        client.publish(MQTT_TOPIC, payload)
        print("Published to ThingSpeak via MQTT:", payload)
        return True
    except Exception as e:
        print("MQTT send error:", e)
        return False

def display_status(temp, humidity):
    oled.fill(0)
    oled.text(f"Temp: {temp:.1f}C", 0, 0)
    oled.text(f"Humid: {humidity:.1f}%", 0, 16)
    oled.show()

def connect_mqtt():
    try:
        client = MQTTClient(client_id=THINGSPEAK_CLIENT_ID,
                            server=THINGSPEAK_MQTT_HOST,
                            port=THINGSPEAK_MQTT_PORT,
                            user=THINGSPEAK_USERNAME,
                            password=THINGSPEAK_MQTT_API_KEY)
        client.connect()
        print("Connected to ThingSpeak MQTT")
        return client
    except Exception as e:
        print("MQTT connection error:", e)
        return None

def main():
    oled.fill(0)
    oled.text("IoT Monitor", 0, 0)
    oled.text("Booting...", 0, 16)
    oled.show()
    print("IoT Monitoring...")
    print("Booting...")

    client = connect_mqtt()
    if not client:
        print("Failed to connect to MQTT broker. Rebooting...")
        machine.reset()

    while True:
        temp, humidity = read_sensor()
        if temp is None or humidity is None:
            print("Failed to read sensor data. Retrying...")
            time.sleep(2)
            continue

        send_success = send_to_thingspeak_mqtt(client, temp, humidity)
        display_status(temp, humidity)
        print(temp, humidity)

        print(f"Waiting {CHECK_INTERVAL} seconds")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()