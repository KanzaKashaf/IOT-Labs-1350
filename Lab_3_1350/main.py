#print("Hello, ESP32-S3!")

#from machine import Pin 
#from machine import Pin, I2C
#import machine
#import ssd1306 
#import dht
#import time

#DHT_PIN = 4  # DHT22 data pin

# Initialize DHT22 sensor
#dht_sensor = dht.DHT22(machine.Pin(DHT_PIN)) # change DHT11 fr physical device

# Initialize OLED display
#i2c = machine.I2C(scl=machine.Pin(9), sda=machine.Pin(8))
#oled = ssd1306.SSD1306_I2C(128, 64, i2c)


# Main loop
#while True:
#    try:
#        dht_sensor.measure()
#        time.sleep(.2)
#        temp = dht_sensor.temperature()
#        humidity = dht_sensor.humidity()
        #print(temp, humidity)
#        oled.fill(0)

        #oled.text("Temp: {} C".format(temp), 0, 0)
        #oled.text("Humidity: {}%".format(humidity), 0, 16)

        #oled.text("Welcome to Iot", 0, 0)
        #oled.text("Kanza Kashaf", 0, 8)
        #oled.text("22-NTU-CS-1350", 0, 16)
        #oled.text("BSAI", 0, 24)
        #oled.text("National Textile", 0, 32)
        #oled.text("University", 0, 40)
        #oled.text("Fasilabad", 0, 48)
        #oled.text("Pakistan", 0, 56)

        #oled.text("Hello Sir", 29, 29)

#        oled.show()

# screen pixels are 128 and 64 .... each alphabet take 8X8 pixels
# horizontally 16 letters vertically 8 letters


#    except Exception as e:
#        print("Error reading DHT22 sensor:", e)
    
        
#    time.sleep(1)  # Update every 2 seconds


print("Hello, ESP32-S3!")

from machine import Pin, I2C, Timer
import machine
import ssd1306 
import dht
import time

DHT_PIN = 4  # DHT22 data pin
button = Pin(0, Pin.IN, Pin.PULL_UP)
# Initialize DHT22 sensor
dht_sensor = dht.DHT22(machine.Pin(DHT_PIN)) # change DHT11 fr physical device

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
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

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
        print("Error reading DHT22 sensor:", e)
      
    time.sleep(1)  # Update every 2 seconds























