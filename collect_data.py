import cv2
import mediapipe as mp
import csv
import time

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='pose_landmarker.task'),
    running_mode=VisionRunningMode.IMAGE
)

cap = cv2.VideoCapture(0)
recording = None
data = []

with PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect(mp_image)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]
            row = []
            for lm in landmarks:
                row.extend([lm.x, lm.y, lm.z])

            if recording is not None:
                row.append(recording)
                data.append(row)

        if recording == 1:
            label_text = "Recording: GOOD posture"
            color = (0, 255, 0)
        elif recording == 0:
            label_text = "Recording: BAD posture"
            color = (0, 0, 255)
        else:
            label_text = "Press G = good posture | B = bad posture | S = save & quit"
            color = (255, 255, 255)

        cv2.putText(frame, label_text, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"Samples: {len(data)}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Data Collection", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('g'):
            recording = 1
        elif key == ord('b'):
            recording = 0
        elif key == ord('s'):
            with open('posture_data.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            print(f"Saved {len(data)} samples to posture_data.csv")
            break

cap.release()
cv2.destroyAllWindows()