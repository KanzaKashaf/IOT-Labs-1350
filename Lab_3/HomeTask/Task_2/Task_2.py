print("Hello, ESP32-S3!")

from machine import Pin, I2C, Timer
import machine
import ssd1306 
import dht
import time

DHT_PIN = 4  # DHT11 data pin
button = Pin(0, Pin.IN, Pin.PULL_UP)
# Initialize DHT11 sensor
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN)) # change DHT11 fr physical device

# Initialize OLED display
i2c = machine.I2C(scl=machine.Pin(9), sda=machine.Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

pressed= False
debounce_timer = None

def button_pressed(pin):
    global  debounce_timer, pressed  # Declare variables as global

    if debounce_timer is None:
        pressed= not pressed
        if pressed:
            oled.poweroff()
           
        else:
            oled.poweron()

        # Start a timer for debounce period (e.g., 200 milliseconds)
        debounce_timer = Timer(0)
        debounce_timer.init(mode=Timer.ONE_SHOT, period=200, callback=debounce_callback)

def debounce_callback(timer):
    global debounce_timer
    debounce_timer = None

# Attach the interrupt to the button's rising edge
#button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

# Main loop
while True:
    try:
        dht_sensor.measure()
        time.sleep(.2)
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        print(temp, humidity)
        oled.fill(0)
        oled.text("Temp: {} C".format(temp), 0, 0)
        oled.text("Humidity: {}%".format(humidity), 0, 16)
        oled.show()

    except Exception as e:
        print("Error reading DHT11 sensor:", e)
      
    time.sleep(1)  # Update every 2 seconds
























