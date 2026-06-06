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

// Variáveis para suavização cinemática (Trapezoidal/Triangular)
float current_angles[5] = {90.0, 90.0, 90.0, 90.0, 90.0};
float current_velocities[5] = {0.0, 0.0, 0.0, 0.0, 0.0};
int target_angles[5] = {90, 90, 90, 90, 90};

const float MAX_VELOCITY = 4.0; // Velocidade máxima
const float ACCELERATION = 0.5; // Aceleração

const int BUFFER_SIZE = 256;
char serial_buffer[BUFFER_SIZE];
int buffer_index = 0;

void set_servo(int channel, int angle) {
    int clamped_angle = constrain(angle, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
    int pulse = map(clamped_angle, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE, SERVO_MIN_PULSE, SERVO_MAX_PULSE);
    int duty = map(pulse, 0, 20000, 0, (1 << LEDC_RESOLUTION) - 1);
    ledcWrite(LEDC_CHANNELS[channel], duty);
}

void setup_servos() {
    for (int i = 0; i < 5; i++) {
        ledcSetup(LEDC_CHANNELS[i], LEDC_FREQ, LEDC_RESOLUTION);
        ledcAttachPin(SERVO_PINS[i], LEDC_CHANNELS[i]);
        set_servo(i, (int)current_angles[i]);
    }
}

void update_servos() {
    for (int i = 0; i < 5; i++) {
        float dist_to_target = target_angles[i] - current_angles[i];
        
        if (abs(dist_to_target) > 0.1) {
            // Cálculo da velocidade de frenagem necessária para parar no alvo
            float v_required_to_stop = sqrt(2.0 * ACCELERATION * abs(dist_to_target));
            
            // Perfil trapezoidal: acelera, cruza na max, desacelera
            float v_setpoint = min(MAX_VELOCITY, v_required_to_stop);
            
            // Ajuste de direção
            if (dist_to_target > 0) {
                current_velocities[i] += ACCELERATION;
                if (current_velocities[i] > v_setpoint) current_velocities[i] = v_setpoint;
            } else {
                current_velocities[i] -= ACCELERATION;
                if (current_velocities[i] < -v_setpoint) current_velocities[i] = -v_setpoint;
            }
            
            current_angles[i] += current_velocities[i];
            
            // Checagem final para evitar overshoot
            if (abs(target_angles[i] - current_angles[i]) < abs(current_velocities[i])) {
                current_angles[i] = target_angles[i];
                current_velocities[i] = 0;
            }
            
            set_servo(i, (int)current_angles[i]);
        } else {
            current_angles[i] = target_angles[i];
            current_velocities[i] = 0;
        }
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
            target_angles[i] = angles[i].as<int>();
        }
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
    update_servos();
    delay(10); 
}
