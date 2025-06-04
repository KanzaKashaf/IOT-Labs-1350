#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <time.h>

// WiFi credentials
const char* ssid = "NTU FSD";
const char* password = "";

// Firebase Config
const String FIREBASE_HOST = "lab11firebaseq2-default-rtdb.firebaseio.com/";
const String FIREBASE_AUTH = "AIzaSyBwSC8iKdBgcGdWii1B8kRXgttIjTamynU";

// Firebase path
const String FIREBASE_PATH = "/sensor_data.json";

// DHT Config
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Timing
const unsigned long SEND_INTERVAL = 10000;
const unsigned long SENSOR_DELAY = 2000;
unsigned long lastSendTime = 0;
unsigned long lastReadTime = 0;

// ======= Setup ======= //
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Firebase + NTP + DHT11");

  connectWiFi();
  initDHT();
  configTime(18000, 0, "pool.ntp.org", "time.nist.gov"); // GMT+5 (Pakistan Time = 5*3600 = 18000)

  Serial.print("Waiting for time sync");
  while (time(nullptr) < 100000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nTime synced!");
}

// ======= Main Loop ======= //
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (millis() - lastReadTime >= SENSOR_DELAY) {
    float temp, hum;
    if (readDHT(&temp, &hum)) {
      if (millis() - lastSendTime >= SEND_INTERVAL) {
        sendToFirebase(temp, hum);
        lastSendTime = millis();
      }
    }
    lastReadTime = millis();
  }
}

// ======= Functions ======= //

void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 20) {
    delay(500);
    Serial.print(".");
    tries++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected.");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi failed.");
  }
}

void initDHT() {
  dht.begin();
  Serial.println("DHT initialized.");
  delay(500);
}

bool readDHT(float* temp, float* hum) {
  *temp = dht.readTemperature();
  *hum = dht.readHumidity();
  if (isnan(*temp) || isnan(*hum)) {
    Serial.println("Failed to read from DHT sensor!");
    return false;
  }
  Serial.printf("Temp: %.1f°C, Humidity: %.1f%%\n", *temp, *hum);
  return true;
}

String getFormattedTime() {
  time_t now = time(nullptr);
  struct tm* timeinfo = localtime(&now);
  char buffer[30];
  strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", timeinfo);
  return String(buffer);
}

void sendToFirebase(float temp, float hum) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
    return;
  }

  HTTPClient http;
  String url = "https://" + FIREBASE_HOST + FIREBASE_PATH + "?auth=" + FIREBASE_AUTH;
  String timestamp = getFormattedTime();

  String json = "{\"temperature\":" + String(temp) +
                ",\"humidity\":" + String(hum) +
                ",\"timestamp\":\"" + timestamp + "\"}";

  Serial.println("Sending JSON:");
  Serial.println(json);

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