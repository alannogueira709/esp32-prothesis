#include <Arduino.h>
#include <ArduinoJson.h>

const int SERVO_PINS[5] = {4, 5, 6, 7, 15};
const int LEDC_CHANNELS[5] = {0, 1, 2, 3, 4};
const int LEDC_FREQ = 50;
const int LEDC_RESOLUTION = 14;

const int SERVO_MIN_PULSE = 500;
const int SERVO_MAX_PULSE = 2500;
const int SERVO_MIN_ANGLE = 0;
const int SERVO_MAX_ANGLE = 180;

const int BUFFER_SIZE = 256;
char serial_buffer[BUFFER_SIZE];
int buffer_index = 0;

void set_servo(int channel, int angle) {
    angle = constrain(angle, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
    int pulse = map(angle, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE, SERVO_MIN_PULSE, SERVO_MAX_PULSE);
    int duty = map(pulse, 0, 20000, 0, (1 << LEDC_RESOLUTION) - 1);
    ledcWrite(LEDC_CHANNELS[channel], duty);
}

void setup_servos() {
    for (int i = 0; i < 5; i++) {
        ledcSetup(LEDC_CHANNELS[i], LEDC_FREQ, LEDC_RESOLUTION);
        ledcAttachPin(SERVO_PINS[i], LEDC_CHANNELS[i]);
        set_servo(i, 90);
    }
}

void parse_and_execute(const char* json_string) {
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, json_string);

    if (error) {
        Serial.print(F("[ERRO] JSON: "));
        Serial.println(error.c_str());
        return;
    }

    JsonArray angles = doc["s"];
    if (angles.size() == 5) {
        for (int i = 0; i < 5; i++) {
            int angle = angles[i].as<int>();
            set_servo(i, angle);
        }
        Serial.print(F("[OK] "));
        for (int i = 0; i < 5; i++) {
            Serial.print(angles[i].as<int>());
            if (i < 4) Serial.print(",");
        }
        Serial.println();
    }

    const char* gesture = doc["g"];
    if (gesture) {
        Serial.print(F("[GESTO] "));
        Serial.println(gesture);
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println(F("[ESP32-S3] Inicializando..."));
    setup_servos();
    Serial.println(F("[ESP32-S3] Pronto. Formato: {\"s\":[0,45,90,135,180],\"g\":\"gesto\"}"));
}

void loop() {
    while (Serial.available() > 0) {
        char c = Serial.read();
        if (c == '\n' || buffer_index >= BUFFER_SIZE - 1) {
            serial_buffer[buffer_index] = '\0';
            if (buffer_index > 0) {
                parse_and_execute(serial_buffer);
            }
            buffer_index = 0;
        } else {
            serial_buffer[buffer_index++] = c;
        }
    }
}
