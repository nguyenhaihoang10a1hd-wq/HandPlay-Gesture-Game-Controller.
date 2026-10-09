from mediapipe.tasks.python import vision
from mediapipe.tasks import python
import time
import mediapipe as mp
import cv2

options = vision.HandLandmarkerOptions(
       base_options=python.BaseOptions(
       model_asset_path=r"C:\Users\DELL\Downloads\hand_landmarker.task"
       ),
       running_mode=vision.RunningMode.VIDEO,
       num_hands=2,
       )
detector = vision.HandLandmarker.create_from_options(options)
start = time.time()

def results(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp_ms = int((time.time() - start) * 1000)
    result = detector.detect_for_video(mp_image, timestamp_ms)
    return result


