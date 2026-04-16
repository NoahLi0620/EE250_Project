import cv2
import mediapipe as mp
import requests
import time
import numpy as np
import tensorflow as tf
import pickle
import sys
RPI_IP = sys.argv[1] if len(sys.argv) > 1 else "172.20.10.7"
RPI_URL = "http://" + RPI_IP + ":5000/posture"

model = tf.keras.models.load_model('posture_model.h5')
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='pose_landmarker.task'),
    running_mode=VisionRunningMode.IMAGE
)
#I ask claude for generate the MediaPipe pose landmarker and how to use it to collect data
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
            row = []
            for lm in landmarks:
                row.extend([lm.x, lm.y, lm.z])

            row = np.array(row).reshape(1, -1)
            row = scaler.transform(row)
            row = row.reshape(1, row.shape[1], 1)

            prob = float(model.predict(row, verbose=0)[0][0])
            status = "Good" if prob >= 0.5 else "Bad"

            color = (0, 255, 0) if prob >= 0.5 else (0, 0, 255)
            cv2.putText(frame, f"Prob: {prob:.2f} | {status}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            if time.time() - last_send > 3:
                try:
                    requests.post(RPI_URL, json={"prob": round(prob, 3), "status": status}, timeout=2)
                    last_send = time.time()
                except:
                    print("Could not reach RPi")

        cv2.imshow("Posture Monitor", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()