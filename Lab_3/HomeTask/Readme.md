# Lab3 - MicroPython Home Tasks

## Home Tasks

###  Task 1: Displaying Temperature & Humidity on OLED
###  Task 1.1
In this task, we simply display the temperature and humidity values on oled by using a DHT11 sensor. We connect the ESP32-S3 with DHT11 sensor and monitor OLED to display the values. 

###  Task 1.2: Try adding emojis
In this task, we try to add emojis in the oled display by pasting emojies with temperature and humidity but our oled does not support it. It show black line insted of emojis.

###  Task 1.3: Try adding emojis
In this, when i blow up the sensor their is the change in humidty. That i can clearly see.

---

### Task 2: Running the Code Without Interrupt 
In this task, when we remove the interrupt the OLED remains ON when we press the button. But when we use interrupt code, and we press button the OLED becomes OFF and if we repressed the button the OLED becomes ON.

---

### Task 3: Understanding Debounce Issue
#### Task 3.1 What is a debounce issue and why we get rid of it? 
A debounce issue occurs when a function triggers too frequently, causing performance problems. We have to get rid of it in order to get optimal solution that we are desired.

#### Tas 3.2 In which applications/domains, debounce issue can be threatening if not resolved in the system?
It will be threatening in:

1. Web and mobile applications: 
That multiple form submission will be occured (duplications)
Multiple transactions whould be made.

2. Embedded Systems:
In home automation, multiple triggers will crash the devices.

3. Financial & Trading Systems
Multiple unintended order placements due to rapid input.
In banking Systems, double withdrawals or transactions will cause due to rapid user actions.

#### Tas 3.3  Why debounce occurs? Is it a compiler error, logical error or micro-controller is cheap?
It occurs due to the nature of the event handling and input signals. It is not due to compiler error. It is a logical issue caused by unintended rapid event triggering.

---

### Task 4: Interrupts understanding
#### Task 4.1 Why we used interrupt?
We use intrupts to make same action's piority more then the other actions. When an intrupts occurs CPU stops continuing working and go to the intrupts function and execute it first.

#### Task 4.2 How does interrupt lower the processing cost of the micro-controller?
Interrupts allow a microcontroller to respond to events only when needed, instead of continuously checking for them. This significantly reduces CPU usage and power consumption.

---

Wokwi Link:
https://wokwi.com/projects/423479258828533761