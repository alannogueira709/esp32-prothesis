import os
import urllib.request
import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from .config import Config

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

GESTURE_COLORS_BGR = {
    "aberta":      (0, 255, 0),
    "fechada":     (0, 0, 255),
    "sinal da paz":(0, 255, 255),
    "like":        (255, 128, 0),
    "faz o L":     (255, 255, 0),
    "ROCK!!":      (255, 0, 255),
}
DEFAULT_COLOR_BGR = (255, 255, 255)


def _ensure_model(path: str) -> str:
    if os.path.isfile(path):
        return path
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    print(f"[HandTracker] Baixando modelo em: {path}")
    urllib.request.urlretrieve(MODEL_URL, path)
    return path


class HandTracker:
    def __init__(self, config: Config):
        self.config = config
        self.cap = cv2.VideoCapture(config.CAMERA_ID, cv2.CAP_DSHOW)
        time.sleep(0.5)
        for _ in range(10):
            if self.cap.isOpened():
                ok, _ = self.cap.read()
                if ok:
                    break
            time.sleep(0.2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        self._frame_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or config.FRAME_WIDTH
        self._frame_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or config.FRAME_HEIGHT

        model_path = _ensure_model(config.HAND_MODEL_PATH)
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=config.MAX_HANDS,
            min_hand_detection_confidence=config.DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.DETECTION_CONFIDENCE,
            min_tracking_confidence=config.TRACKING_CONFIDENCE,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def _draw_landmarks(self, frame, landmarks, color):
        pts = []
        min_x = self._frame_w
        max_x = 0
        min_y = self._frame_h
        max_y = 0
        for lm in landmarks:
            x = self._frame_w - int(lm.x * self._frame_w)
            y = int(lm.y * self._frame_h)
            pts.append((x, y))
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
        
        # Bounding box
        padding = 20
        cv2.rectangle(frame, (min_x - padding, min_y - padding), (max_x + padding, max_y + padding), color, 2)
        
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], color, 2)
        for p in pts:
            cv2.circle(frame, p, 3, color, -1)

    def _draw_overlay(self, frame, info):
        if not info:
            return
        lines = []
        lines.append(f"Dedos levantados: {info.get('fingers', 0)}")
        gesture = info.get("gesture") or "-"
        lines.append(f"Gesto: {gesture}")
        angles = info.get("angles")
        if angles is not None:
            lines.append(f"Angulos: {list(angles)}")
        payload = info.get("json")
        if payload:
            lines.append(f"JSON: {payload}")

        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.55
        thickness = 1
        line_h = 22
        pad = 10
        max_w = 0
        for ln in lines:
            (w, _), _ = cv2.getTextSize(ln, font, scale, thickness)
            if w > max_w:
                max_w = w
        box_w = max_w + pad * 2
        box_h = line_h * len(lines) + pad * 2
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (box_w, box_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        y = pad + 16
        for ln in lines:
            color = GESTURE_COLORS_BGR.get(gesture, DEFAULT_COLOR_BGR) if "Gesto:" in ln else (255, 255, 255)
            cv2.putText(frame, ln, (pad, y), font, scale, color, thickness, cv2.LINE_AA)
            y += line_h

    def detect(self):
        success, frame = self.cap.read()
        if not success:
            return None, None, None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self.detector.detect(mp_image)
        landmarks = result.hand_landmarks[0] if result.hand_landmarks else None
        handedness = result.handedness[0][0].category_name if result.handedness else None
        return landmarks, handedness, frame

    def draw(self, frame, landmarks, info=None):
        if self.config.SHOW_PREVIEW and frame is not None:
            display = cv2.flip(frame, 1)
            if landmarks is not None:
                gesture = (info or {}).get("gesture")
                color = GESTURE_COLORS_BGR.get(gesture, DEFAULT_COLOR_BGR)
                self._draw_landmarks(display, landmarks, color)
            self._draw_overlay(display, info)
            cv2.imshow(self.config.WINDOW_NAME, display)

    def process(self):
        landmarks, frame = self.detect()
        self.draw(frame, landmarks)
        return landmarks, frame

    def release(self):
        self.detector.close()
        self.cap.release()
        cv2.destroyAllWindows()
