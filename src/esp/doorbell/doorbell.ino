#include <ESP8266WiFi.h>

const uint8_t POWER_PIN = 12;

const char* SSID   = "<SSID-HERE>";
const char* PASSWD = "<PASSWORD-HERE>";

bool CAN_EXIT = true;

void setup() {
    Serial.begin(115200);

    pinMode(POWER_PIN, OUTPUT);
    digitalWrite(POWER_PIN, HIGH);

    delay(100);

    // Connecting WiFi
    Serial.println();
    Serial.print("Connecting to ");
    Serial.print(SSID);
    WiFi.begin(SSID, PASSWD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(200);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("WiFi connected, ");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.println();
    Serial.flush();
}

void loop() {
    if (CAN_EXIT) {
        // Power off
        Serial.println("Powering down now!");
        Serial.flush();
        delay(100);
        digitalWrite(POWER_PIN, LOW);
    }
}
