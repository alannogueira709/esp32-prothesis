import math
from .config import Config
class GestureRecognizer:
    def __init__(self, config: Config):
        self.config = config
    def recognize(self, landmarks):
        if not landmarks:
            return None, None
        h, w = 1, 1
        palm_width = self._dist(landmarks[5], landmarks[17])
        angles = []
        finger_openness = {}
        for name, (tip, mcp, _) in self.config.DEDOS.items():
            tip_pt = landmarks[tip]
            mcp_pt = landmarks[mcp]
            if name == "polegar":
                openness = self._check_thumb_openness(landmarks)
            else:
                openness = self._dist(tip_pt, mcp_pt) / palm_width
                openness = min(max(openness, 0.0), 1.0)
            finger_openness[name] = openness
            angle = int(self._map_range(
                openness,
                0.0, 1.0,
                self.config.SERVO_MAX, self.config.SERVO_MIN
            ))
            angles.append(angle)
        gesture = self._classify_gesture(finger_openness)
        return angles, gesture, finger_openness

    def _check_thumb_openness(self, landmarks):
        thumb_tip = landmarks[4]
        thumb_base = landmarks[2]
        index_mcp = landmarks[5]
        v_thumb = (thumb_tip.x - thumb_base.x, thumb_tip.y - thumb_base.y, thumb_tip.z - thumb_base.z)
        v_palm = (index_mcp.x - thumb_base.x, index_mcp.y - thumb_base.y, index_mcp.z - thumb_base.z)
        dot_product = v_thumb[0] * v_palm[0] + v_thumb[1] * v_palm[1] + v_thumb[2] * v_palm[2]
        mag_thumb = math.sqrt(v_thumb[0]**2 + v_thumb[1]**2 + v_thumb[2]**2)
        mag_palm = math.sqrt(v_palm[0]**2 + v_palm[1]**2 + v_palm[2]**2)
        if mag_thumb == 0 or mag_palm == 0:
            return 0
        cos_angle = dot_product / (mag_thumb * mag_palm)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angle = math.degrees(math.acos(cos_angle))
        return min(max((angle - 30) / (70 - 30), 0.0), 1.0)

    def _dist(self, a, b):
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)
    def _map_range(self, value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    def _classify_gesture(self, finger):
        open_count = sum(
            1 for v in finger.values()
            if v > self.config.GESTURE_THRESHOLD_OPEN
        )
        closed_count = sum(
            1 for v in finger.values()
            if v < self.config.GESTURE_THRESHOLD_CLOSED
        )
        if open_count >= 4:
            return "aberta"
        if closed_count >= 4:
            return "fechada"
        if finger["indicador"] > self.config.GESTURE_THRESHOLD_OPEN and \
           finger["meio"] > self.config.GESTURE_THRESHOLD_OPEN and \
           finger["anelar"] < self.config.GESTURE_THRESHOLD_CLOSED and \
           finger["mindinho"] < self.config.GESTURE_THRESHOLD_CLOSED:
            return "sinal da paz"
        if finger["polegar"] > 0.6 and \
           all(finger[f] < self.config.GESTURE_THRESHOLD_CLOSED
               for f in ("indicador", "meio", "anelar", "mindinho")):
            return "like"
        if finger["polegar"] > self.config.GESTURE_THRESHOLD_OPEN and \
           finger["indicador"] > self.config.GESTURE_THRESHOLD_OPEN and \
              all(finger[f] < self.config.GESTURE_THRESHOLD_CLOSED
                for f in ("meio", "anelar", "mindinho")):
                return "faz o L"
        if finger["polegar"] > self.config.GESTURE_THRESHOLD_OPEN and \
           finger["indicador"] > self.config.GESTURE_THRESHOLD_OPEN and \
           finger["mindinho"] > self.config.GESTURE_THRESHOLD_OPEN and \
              all(finger[f] < self.config.GESTURE_THRESHOLD_CLOSED
                for f in ("meio", "anelar")):
                return "ROCK!!"
        return None;