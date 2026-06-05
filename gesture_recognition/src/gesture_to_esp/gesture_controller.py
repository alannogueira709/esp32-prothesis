import json
import cv2
from .config import Config, interactive_setup
from .hand_tracker import HandTracker
from .gesture_recognizer import GestureRecognizer
from .serial_comm import SerialComm

OPEN_THRESHOLD = 0.6


class GestureController:
    def __init__(self, config: Config = None):
        if config is None:
            config = Config()
        if config.SERIAL_PORT is None or config.SERIAL_TIMEOUT is None:
            config = interactive_setup(config)
        self.config = config
        self.tracker = HandTracker(self.config)
        self.recognizer = GestureRecognizer(self.config)
        self.comm = SerialComm(self.config)

    def _count_fingers(self, finger_openness):
        if not finger_openness:
            return 0
        return sum(1 for v in finger_openness.values() if v > OPEN_THRESHOLD)

    def run(self):
        print("[Controle] Iniciando controle gestual...")
        print("[Controle] Pressione ESC para sair")
        while True:
            landmarks, frame = self.tracker.detect()
            angles = None
            gesture = None
            fingers = 0
            payload_json = None

            if landmarks:
                angles, gesture, finger_openness = self.recognizer.recognize(landmarks)
                if angles:
                    fingers = self._count_fingers(finger_openness)
                    self.comm.send(angles, gesture)
                    payload = self.comm.build_payload(angles, gesture)
                    payload_json = json.dumps(payload, separators=(",", ":"))

            info = {
                "fingers": fingers,
                "gesture": gesture,
                "angles": angles,
                "json": payload_json,
            }
            self.tracker.draw(frame, landmarks, info)

            if self.config.SHOW_PREVIEW:
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    break
        self.stop()

    def stop(self):
        self.tracker.release()
        self.comm.close()
        print("[Controle] Recursos liberados.")
