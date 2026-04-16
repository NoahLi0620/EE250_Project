import cv2
import mediapipe as mp
import requests
import time

RPI_URL = "http://172.20.10.7:5000/posture"

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='pose_landmarker.task'),
    running_mode=VisionRunningMode.IMAGE
)

cap = cv2.VideoCapture(0)
last_send = 0

with PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect(mp_image)

        prob = 0.0
        status = "No pose detected"

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            nose = landmarks[0]

            shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
            shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2
            head_offset = abs(nose.x - shoulder_mid_x)

            score = 100 - (shoulder_diff * 300) - (head_offset * 200)
            score = max(0, min(100, score))
            prob = round(score / 100, 3)
            status = "Good" if prob >= 0.7 else "Bad"

            color = (0, 255, 0) if status == "Good" else (0, 0, 255)
            cv2.putText(frame, "BASIC MODE | Score: " + str(round(score)) + " | " + status,
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if time.time() - last_send > 3:
                try:
                    requests.post(RPI_URL, json={"prob": prob, "status": status}, timeout=2)
                    last_send = time.time()
                except:
                    print("Could not reach RPi")

        cv2.imshow("Posture Monitor - Basic", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()