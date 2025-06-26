#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"
#include <Adafruit_ADXL345_U.h>
#include <ClosedCube_MAX30205.h>
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "model_data.h"
#include <time.h>

// WiFi credentials
const char* ssid = "NTU FSD";
const char* password = "";
const String USER_UID = "NN4WDAbitlXXPefpPi8BFmL0etV2";

// Firebase Config
const String FIREBASE_HOST = "senseai-db-a95b9-default-rtdb.firebaseio.com";
const String FIREBASE_AUTH = "bpS289o5XH3TEcst0m4wIlaEbt4F95f6gRwxWIVI";
const String FIREBASE_PATH = "/users/" + USER_UID + "/rawSensorData.json";

// Sensor Config
#define SDA_PIN 8
#define SCL_PIN 9
#define BUFFER_SIZE 100

MAX30105 pulseSensor;
Adafruit_ADXL345_Unified accel(12345);
ClosedCube_MAX30205 tempSensor;

uint32_t irBuf[BUFFER_SIZE], redBuf[BUFFER_SIZE];

// TensorFlow Lite Micro
constexpr int kTensorArenaSize = 10 * 1024;
uint8_t tensor_arena[kTensorArenaSize];

const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
tflite::MicroMutableOpResolver<3> resolver;
TfLiteTensor* input = nullptr;
TfLiteTensor* output = nullptr;

// Timing
const unsigned long SEND_INTERVAL = 10000;
unsigned long lastSendTime = 0;

// Accelerometer normalization (adjust according to your dataset)
float X_MIN = -17.0, X_MAX = 17.0;
float Y_MIN = -17.0, Y_MAX = 17.0;

// ==================== SETUP ==================== //
void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);

  connectWiFi();
  configTime(18000, 0, "pool.ntp.org", "time.nist.gov");  // GMT+5

  while (time(nullptr) < 100000) delay(500);
  Serial.println("Time synced!");

  // Sensors Initialization
  if (!pulseSensor.begin(Wire, I2C_SPEED_FAST)) while (1) Serial.println("MAX30102 not found!");
  pulseSensor.setup(0x1F, 1, 2, 100, 411, 4096);
  Serial.println("MAX30102 OK");

  if (!accel.begin()) while (1) Serial.println("ADXL345 not found!");
  accel.setRange(ADXL345_RANGE_16_G);
  Serial.println("ADXL345 OK");

  tempSensor.begin(0x48);
  Serial.println("MAX30205 OK");

  resetMAX30205();

  // TensorFlow Lite setup
  model = tflite::GetModel(model_tflite);
  resolver.AddFullyConnected();
  resolver.AddRelu();
  resolver.AddLogistic();

  static tflite::MicroInterpreter static_interpreter(model, resolver, tensor_arena, kTensorArenaSize);
  interpreter = &static_interpreter;

  if (interpreter->AllocateTensors() != kTfLiteOk) {
    Serial.println("Tensor allocation failed"); while (1);
  }
  input = interpreter->input(0);
  output = interpreter->output(0);

  Serial.println("Setup complete.");
}

// ==================== LOOP ==================== //
void loop() {
  if (millis() - lastSendTime >= SEND_INTERVAL) {
    uploadDataToFirebase();
    lastSendTime = millis();
  }
}

// ==================== FUNCTIONS ==================== //

void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
}

void resetMAX30205() {
  Wire.beginTransmission(0x48);
  Wire.write(0x01);
  Wire.write(0x80);
  Wire.endTransmission();
  delay(100);
}

String getFormattedTime() {
  time_t now = time(nullptr);
  struct tm* timeinfo = localtime(&now);
  char buffer[30];
  strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", timeinfo);
  return String(buffer);
}

void uploadDataToFirebase() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
    connectWiFi();
    return;
  }

  // ==================== READ SENSORS ==================== //
  float temperature = tempSensor.readTemperature();
  if (temperature < 10.0 || temperature > 45.0) {
    Serial.println("MAX30205 error! Retrying...");
    
    delay(100);
    resetMAX30205();  // Reset sensor before retry
    temperature = tempSensor.readTemperature();
    
    if (temperature < 10.0 || temperature > 45.0) {
      Serial.println("MAX30205 failed after retry. Setting temperature=null.");
      temperature = NAN;  // Mark as invalid
    }
  }

  // 2. Accelerometer
  sensors_event_t event;
  accel.getEvent(&event);
  float accel_x = event.acceleration.x;
  float accel_y = event.acceleration.y;

  // Normalize
  input->data.f[0] = (accel_x - X_MIN) / (X_MAX - X_MIN);
  input->data.f[1] = (accel_y - Y_MIN) / (Y_MAX - Y_MIN);

  interpreter->Invoke();
  float fall_probability = output->data.f[0];
  String fall_status = (fall_probability > 0.5) ? "Fall Detected" : "Stable";

  // 3. MAX30102 Pulse Sensor
  for (int i = 0; i < BUFFER_SIZE; i++) {
    while (!pulseSensor.available()) pulseSensor.check();
    redBuf[i] = pulseSensor.getRed();
    irBuf[i] = pulseSensor.getIR();
    pulseSensor.nextSample();
  }

  int32_t spo2, hr;
  int8_t spo2Valid, hrValid;
  maxim_heart_rate_and_oxygen_saturation(irBuf, BUFFER_SIZE, redBuf, &spo2, &spo2Valid, &hr, &hrValid);

  String timestamp = getFormattedTime();

  // ==================== BUILD JSON ==================== //
  String json = "{";
  json += "\"temperature\":";
  json += isnan(temperature) ? "null" : String(temperature, 2);
  json += ",";
  json += "\"accel_x\":" + String(accel_x, 2) + ",";
  json += "\"accel_y\":" + String(accel_y, 2) + ",";
  json += "\"fall_probability\":" + String(fall_probability, 4) + ",";
  json += "\"fall_status\":\"" + fall_status + "\",";
  json += "\"heartrate\":";
  json += (hrValid) ? String(hr) : "null";
  json += ",";
  json += "\"spo2\":";
  json += (spo2Valid) ? String(spo2) : "null";
  json += ",";
  json += "\"timestamp\":\"" + timestamp + "\"";
  json += ",\"user_id\":\"" + USER_UID + "\"}";
  
  Serial.println("Sending JSON:");
  Serial.println(json);

  // ==================== SEND TO FIREBASE ==================== //
  HTTPClient http;
  String url = "https://" + FIREBASE_HOST + FIREBASE_PATH + "?auth=" + FIREBASE_AUTH;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(json);
  if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_CREATED) {
    Serial.println("Data sent to Firebase successfully.");
  } else {
    Serial.printf("Firebase Error. Code: %d\n", httpCode);
  }
  http.end();
}