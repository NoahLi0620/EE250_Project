from flask import Flask, request, jsonify
import datetime
import threading
import time

app = Flask(__name__)
posture_log = []

bad_streak = 0
BAD_THRESHOLD = 5
buzzer_pin = 17
buzzer_active = False

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzer_pin, GPIO.OUT)
    gpio_available = True
except:
    gpio_available = False
    print("GPIO not available, buzzer disabled")

def buzz(duration=1.0):
    if gpio_available:
        GPIO.output(buzzer_pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(buzzer_pin, GPIO.LOW)

@app.route('/posture', methods=['POST'])
def receive_posture():
    global bad_streak, buzzer_active

    data = request.get_json()
    data['timestamp'] = datetime.datetime.now().strftime('%H:%M:%S')
    posture_log.append(data)

    if data['status'] == 'Bad':
        bad_streak += 1
    else:
        bad_streak = 0

    print(f"[{data['timestamp']}] Prob: {data['prob']} | Status: {data['status']} | Bad streak: {bad_streak}")

    if bad_streak >= BAD_THRESHOLD and not buzzer_active:
        buzzer_active = True
        print("BAD POSTURE ALERT!")
        t = threading.Thread(target=buzz, args=(2.0,))
        t.start()
    elif data['status'] == 'Good':
        buzzer_active = False

    return jsonify({'ok': True, 'bad_streak': bad_streak})

@app.route('/log', methods=['GET'])
def get_log():
    return jsonify(posture_log)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)