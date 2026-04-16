Team Members: Tianyi Li; Hasmik

Project: Smart Posture Monitor
A real-time posture detection system using MediaPipe and a 1D CNN model.
The laptop captures webcam frames, extracts body keypoints, and sends data
to a Raspberry Pi server via HTTP. The RPi logs posture data and serves
a live web dashboard accessible from any browser on the same network.

=== REQUIREMENTS ===

Laptop:
- Python 3.10 or 3.11 recommended (not 3.13)
- Windows / Mac / Linux

Raspberry Pi:
- Raspberry Pi 4 Model B
- Python 3.7+
- Connected to the same WiFi network as the laptop

=== RASPBERRY PI SETUP ===

1. SSH into the Raspberry Pi:
   ssh pi@<RPI_IP>

2. Install dependencies:
   pip3 install flask

3. Transfer server.py to the Raspberry Pi (run on laptop):
   scp server.py pi@<RPI_IP>:~/server.py

4. Run the server:
   python3 server.py

5. Server will be running at:
   http://<RPI_IP>:5000

=== LAPTOP SETUP ===

1. Install dependencies:
   pip install mediapipe==0.10.33 opencv-python requests tensorflow scikit-learn pandas

2. Download the MediaPipe pose landmarker model:
   curl -o pose_landmarker.task https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task

=== RUNNING THE SYSTEM ===

Option A - ML-based client (1D CNN inference):
   python client.py <RPI_IP>

Option B - Rule-based client (no ML, for comparison):
   python client_Basic.py <RPI_IP>

To view the live dashboard, open a browser and go to:
   http://<RPI_IP>:5000

=== TO COLLECT NEW TRAINING DATA ===

1. Run:
   python collect_data.py

2. Controls:
   G = start recording good posture
   B = start recording bad posture
   S = save data and quit

3. Data will be saved to posture_data.csv

=== TO RETRAIN THE MODEL ===

1. Make sure posture_data.csv exists
2. Run:
   python train_model.py
3. Trained model will be saved as posture_model.h5 and scaler.pkl

=== FILE DESCRIPTIONS ===

client.py          - Main client, uses trained 1D CNN to classify posture
client_Basic.py    - Rule-based client, no ML required
collect_data.py    - Tool for collecting posture training data
train_model.py     - Trains the 1D CNN model on collected data
server.py          - Flask server that runs on the Raspberry Pi
posture_data.csv   - Collected training data
posture_model.h5   - Trained CNN model
scaler.pkl         - Data scaler used during inference
pose_landmarker.task - MediaPipe pose detection model (Google)

=== EXTERNAL LIBRARIES ===

Laptop:
- mediapipe==0.10.33   (pose keypoint extraction)
- opencv-python        (webcam capture)
- requests             (HTTP communication)
- tensorflow           (CNN model training and inference)
- scikit-learn         (data preprocessing)
- pandas               (data loading)

Raspberry Pi:
- flask                (HTTP server and dashboard)

=== NOTE ON AI TOOL USAGE ===
There are several places that I use AI to think and generate code: first, in client.py I ask claude for  generate the MediaPipe pose landmarker and how to use it to collect data
second, in train_model I use AI to think and generate the code for using 1D CNN and how many kernels should I use. Third, in server part I use AI to generate the frontend code.
