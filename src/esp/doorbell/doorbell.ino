#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const uint8_t POWER_PIN = 12;

const char* SSID   = "<SSID-HERE>";
const char* PASSWD = "<PASSWORD-HERE>";
const char* SERVER_URL = "http://<server-address>/ding";

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
    Serial.println("WiFi Connected!");
    Serial.printf("IP address: %s\n", WiFi.localIP().toString().c_str());
    WiFi.printDiag(Serial);
    Serial.println();
    Serial.flush();
}

void loop() {
    HTTPClient http;
    Serial.println("Sending ding signal.");
    http.begin(SERVER_URL);
    int respCode = http.POST("{\"bell\":\"<bellid>\"}");
    Serial.println("Sent!");
    Serial.printf("Response: %d\n" ,respCode);

    if (respCode >= 200 && respCode < 300) {
        Serial.println(http.getString());
        CAN_EXIT = true;
    } else {
        Serial.printf("Error: %s\n", http.errorToString(respCode).c_str());
    }

    if (CAN_EXIT) {
        // Power off
        Serial.println("Powering down now!");
        Serial.flush();
        delay(100);
        digitalWrite(POWER_PIN, LOW);
    }
}
