import json
import time

import serial

from .config import Config


class SerialComm:
    def __init__(self, config: Config):
        self.config = config
        self.last_send = 0
        self.last_payload = None
        self.ser = None
        try:
            self.ser = serial.Serial(
                port=config.SERIAL_PORT,
                baudrate=config.SERIAL_BAUD,
                timeout=config.SERIAL_TIMEOUT,
            )
            print(f"[Serial] Conectado em {config.SERIAL_PORT} a {config.SERIAL_BAUD} baud")
        except serial.SerialException as e:
            print(f"[Serial] Erro ao conectar: {e}")

    def build_payload(self, angles, gesture=None):
        payload = {"s": angles}
        if gesture:
            payload["g"] = gesture
        return payload

    def send(self, angles, gesture=None):
        if not self.ser or not self.ser.is_open:
            return False
        now = time.time()
        if now - self.last_send < self.config.SEND_INTERVAL:
            return False
        self.last_send = now
        payload = self.build_payload(angles, gesture)
        self.last_payload = payload
        try:
            line = json.dumps(payload) + "\n"
            self.ser.write(line.encode("utf-8"))
            return True
        except serial.SerialException as e:
            print(f"[Serial] Erro ao enviar: {e}")
            return False

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
