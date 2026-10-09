import cv2
from pynput.keyboard import Controller
from signaturehand import update_held_keys,detect_gesture
from System_specifications import results
import time

keyboard = Controller()
SWAP_HANDS = False

CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
]
TAP_INTERVAL = 0.1
# ---- Cấu hình ----
REQUIRED_FRAMES = 1   # số khung hình liên tiếp thấy cử chỉ mới tính (chống nhiễu)
RELEASE_FRAMES = 1    # số khung hình liên tiếp mất cử chỉ mới nhả phím (chống nhả nhầm)

cap = cv2.VideoCapture(0)

# Mỗi cử chỉ ứng với một nhóm phím được GIỮ cùng lúc
GESTURE_KEYS = {
    "w": ["w"],
    "a": ["a"],
    "d": ["d"],
    "kd": ["k", "d"],
    "ka": ["k", "a"],
    "s":["s"],
    "u":["u"],
    "l":["l"]
}

seen_frames = {g: 0 for g in GESTURE_KEYS}  # số khung liên tiếp THẤY cử chỉ
lost_frames = {g: 0 for g in GESTURE_KEYS}  # số khung liên tiếp MẤT cử chỉ
active = {g: False for g in GESTURE_KEYS}  # cử chỉ đang được kích hoạt
held = set()  # các phím đang được giữ
last_tap = 0.0  # thời điểm bấm liên tục gần nhất

try:
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        result = results(frame)
        h, w, _ = frame.shape
        gestures = {g: False for g in GESTURE_KEYS}
        for hand, handedness in zip(result.hand_landmarks, result.handedness):
            pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand]
            for a, b in CONNECTIONS:
                cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
            for p in pts:
                cv2.circle(frame, p, 4, (0, 0, 255), -1)

            # Ảnh đã lật gương nên nhãn của MediaPipe khớp với tay thật của người dùng
            side = handedness[0].category_name
            if SWAP_HANDS:
                side = "Right" if side == "Left" else "Left"

            name = detect_gesture(hand,side)
            if name in gestures:
                gestures[name] = True
# Không thấy bàn tay nào -> reset trạng thái và nhả hết phím
        if not result.hand_landmarks:
            for g in GESTURE_KEYS:
                seen_frames[g] = 0
                lost_frames[g] = 0
                active[g] = False
            for k in held:
                keyboard.release(k)
            held = set()

# Cập nhật trạng thái từng cử chỉ (có chống nhiễu cả lúc bật và lúc tắt)
        for name, seen in gestures.items():
            if seen:
                seen_frames[name] += 1
                lost_frames[name] = 0
                if seen_frames[name] >= REQUIRED_FRAMES:
                    active[name] = True
            else:
                seen_frames[name] = 0
                lost_frames[name] += 1
                if lost_frames[name] >= RELEASE_FRAMES:
                    active[name] = False

        # Gom các phím cần giữ từ những cử chỉ đang kích hoạt
        desired = set()
        active_labels = []
        for name, is_on in active.items():
            if is_on:
                desired.update(GESTURE_KEYS[name])
                active_labels.append("+".join(k.upper() for k in GESTURE_KEYS[name]))

        held = update_held_keys(desired, held)

        if active_labels:
            status, color = "Dang giu: " + ", ".join(active_labels), (0, 255, 0)
        else:
            status, color = "Khong co cu chi", (0, 0, 255)
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Hand Landmarker", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    # Luôn nhả hết phím khi thoát (kể cả khi lỗi) để tránh bị kẹt phím
    for k in held:
        keyboard.release(k)
    cap.release()
    cv2.destroyAllWindows()