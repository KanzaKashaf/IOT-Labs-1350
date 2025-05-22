import machine
import dht
import time
import _thread
from machine import Pin, SoftI2C, RTC
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

# ==== Config ====
THINGSPEAK_MQTT_HOST = "mqtt3.thingspeak.com"
THINGSPEAK_MQTT_PORT = 1883

THINGSPEAK_CHANNEL_ID = "2970621"
# got after creating mqtt device
THINGSPEAK_CLIENT_ID = "DTIJOw07IwM6ETwmPSAwJh4"
THINGSPEAK_USERNAME = "DTIJOw07IwM6ETwmPSAwJh4"
THINGSPEAK_MQTT_API_KEY = "tkkLiyXk0MzlEqbJi4yC6ESL"

DHT_PIN = 4
CHECK_INTERVAL = 20
MQTT_TOPIC = f"channels/{THINGSPEAK_CHANNEL_ID}/publish"

# ==== Global Variables ====
temp, humidity = 0, 0
oled_lock = _thread.allocate_lock()

# ==== Hardware Init ====
dht_sensor = dht.DHT11(Pin(DHT_PIN))
i2c = SoftI2C(scl=Pin(9), sda=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)



# ==== MQTT Setup ====
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

# ==== Sensor Task (Core 0) ====
def sensor_task():
    global temp, humidity
    client = connect_mqtt()
    if not client:
        machine.reset()

    while True:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            humidity = dht_sensor.humidity()
        except Exception as e:
            print("Sensor read error:", e)
            time.sleep(2)
            continue

        try:
            payload = f"field1={temp}&field2={humidity}"
            client.publish(MQTT_TOPIC, payload)
            print("MQTT Publish:", payload)
        except Exception as e:
            print("MQTT send error:", e)
            try:
                client.connect()
                client.publish(MQTT_TOPIC, payload)
                print("Re-published after reconnect.")
            except:
                print("Re-publish failed.")

        time.sleep(CHECK_INTERVAL)

# ==== OLED Task (Core 1) ====
def oled_task():
    global temp, humidity
    while True:
        oled_lock.acquire()
        oled.fill(0)
        oled.text("IoT Monitor", 0, 0)
        oled.text("Temp: {:.1f}C".format(temp), 0, 16)
        oled.text("Hum: {:.1f}%".format(humidity), 0, 32)
        oled.show()
        oled_lock.release()
        time.sleep(1)

# ==== Main Entry ====
def main():
    oled.fill(0)
    oled.text("Booting...", 0, 0)
    oled.show()
    print("Booting...")

    
    print("Starting OLED thread on core 1...")
    _thread.start_new_thread(oled_task, ())

    print("Starting sensor loop on core 0...")
    sensor_task()  # This stays on main thread

if __name__ == "__main__":
    main()