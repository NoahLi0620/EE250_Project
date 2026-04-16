from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)
posture_log = []
bad_streak = 0

@app.route('/posture', methods=['POST'])
def receive_posture():
    global bad_streak
    data = request.get_json()
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    data['timestamp'] = ts
    posture_log.append(data)

    if data['status'] == 'Bad':
        bad_streak += 1
    else:
        bad_streak = 0

    print("[" + ts + "] Prob: " + str(data['prob']) + " | Status: " + str(data['status']) + " | Bad streak: " + str(bad_streak))
    return jsonify({'ok': True, 'bad_streak': bad_streak})

@app.route('/log', methods=['GET'])
def get_log():
    return jsonify(posture_log)
# I use AI to generate the frontend code especially the css.

@app.route('/')
def dashboard():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Posture Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .status-box { padding: 20px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0; }
        .good { background: #d4edda; color: #155724; }
        .bad { background: #f8d7da; color: #721c24; }
        .neutral { background: #e2e3e5; color: #383d41; }
        .alert { background: #fff3cd; color: #856404; padding: 15px; border-radius: 8px; margin: 10px 0; display: none; }
        .stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 20px 0; }
        .stat-card { background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .stat-num { font-size: 28px; font-weight: bold; color: #333; }
        .stat-label { font-size: 13px; color: #666; margin-top: 4px; }
        canvas { background: white; border-radius: 8px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <h1>Posture Monitor Dashboard</h1>
    <div id="status-box" class="status-box neutral">Waiting for data...</div>
    <div id="alert" class="alert">Bad posture detected for too long! Please sit up straight.</div>
    <div class="stats">
        <div class="stat-card">
            <div class="stat-num" id="total">0</div>
            <div class="stat-label">Total Readings</div>
        </div>
        <div class="stat-card">
            <div class="stat-num" id="good-count" style="color:#155724">0</div>
            <div class="stat-label">Good Posture</div>
        </div>
        <div class="stat-card">
            <div class="stat-num" id="bad-count" style="color:#721c24">0</div>
            <div class="stat-label">Bad Posture</div>
        </div>
    </div>
    <canvas id="chart"></canvas>
    <script>
        const ctx = document.getElementById('chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Posture Probability',
                    data: [],
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76,175,80,0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                scales: {
                    y: { min: 0, max: 1, title: { display: true, text: 'Good Posture Probability' } }
                }
            }
        });

        async function update() {
            const res = await fetch('/log');
            const data = await res.json();
            if (data.length === 0) return;
            const last = data[data.length - 1];
            const box = document.getElementById('status-box');
            box.textContent = last.status + ' - Probability: ' + (last.prob * 100).toFixed(1) + '%';
            box.className = 'status-box ' + (last.status === 'Good' ? 'good' : 'bad');
            const recent = data.slice(-30);
            const badStreak = recent.slice(-5).every(function(d) { return d.status === 'Bad'; });
            document.getElementById('alert').style.display = badStreak ? 'block' : 'none';
            const good = data.filter(function(d) { return d.status === 'Good'; }).length;
            const bad = data.filter(function(d) { return d.status === 'Bad'; }).length;
            document.getElementById('total').textContent = data.length;
            document.getElementById('good-count').textContent = good;
            document.getElementById('bad-count').textContent = bad;
            chart.data.labels = recent.map(function(d) { return d.timestamp; });
            chart.data.datasets[0].data = recent.map(function(d) { return d.prob; });
            chart.data.datasets[0].pointBackgroundColor = recent.map(function(d) { return d.status === 'Good' ? '#4CAF50' : '#f44336'; });
            chart.update();
        }

        update();
        setInterval(update, 3000);
    </script>
</body>
</html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)