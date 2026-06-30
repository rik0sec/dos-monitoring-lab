"""
[LAB] DoS Target Website — Flask
Website target untuk demonstrasi Denial of Service.
Memiliki endpoint ringan dan endpoint berat (heavy computation).
HANYA untuk keperluan edukasi di lingkungan lab lokal.

Jalankan: python website.py
Akses   : http://localhost:5004
"""

import time
import math
import psutil
import threading
from flask import Flask, request, jsonify
from collections import deque

# Thread-safe counter menggunakan Lock
_counter_lock = threading.Lock()
_request_count = 0
_fast_count = 0
_heavy_count = 0

_request_log = deque(maxlen=50)
_rps_history = deque(maxlen=30)
_rps_samples = deque(maxlen=5)
_start_time = time.time()
_last_count = 0

_attack_history = deque(maxlen=50)

_attack_count = 0

_last_attack_time = 0

_attack_active = False

_attack_started = None

app = Flask(__name__)


@app.before_request
def count_requests():
    if request.path == "/stats":
        return
    
    global _request_count
    with _counter_lock:
        _request_count += 1

    _request_log.append({
    "time": time.strftime("%H:%M:%S"),
    "path": request.path,
    "ip": request.remote_addr,
    "method": request.method,
    "query": request.query_string.decode()
})


@app.route("/")
def index():
    return """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Cyber Security Monitoring Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{
    background:#0b1220;
    color:white;
}
.card{
    background:#162033;
    border:1px solid #334155;
    color:white;
}

.card h2{
    color:#ffffff;
    font-weight:bold;
}

.card h6{
    color:#cbd5e1;
}
h2,h3,h4,h5,h6,p,span{
    color:white;
}
.alert-banner{
    font-weight:bold;
    font-size:18px;
}
table{
    color:white !important;
}
</style>
</head>
<body>
<div class="container py-4">
<h2 class="mb-4">🛡 Cyber Security Monitoring Dashboard</h2>
<div id="alert" class="alert alert-success alert-banner">NORMAL TRAFFIC</div>
<div class="row g-3">
<div class="col-md-3">
<div class="card p-3">
<h6>Total Requests</h6>
<h2 id="req">0</h2>
</div>
</div>
<div class="col-md-3">
<div class="card p-3">
<h6>Requests/sec</h6>
<h2 id="rps">0</h2>
</div>
</div>
<div class="col-md-3">
<div class="card p-3">
<h6>Uptime</h6>
<h2 id="uptime">0s</h2>
</div>
</div>
<div class="col-md-3">
<div class="card p-3">
<h6>Status</h6>
<h2 id="status">NORMAL</h2>
</div>
</div>
<div class="col-md-3">
<div class="card p-3">
<h6>CPU Usage</h6>
<h2 id="cpu">0%</h2>
</div>
</div>
<div class="col-md-3">
<div class="card p-3">
<h6>RAM Usage</h6>
<h2 id="ram">0%</h2>
</div>
</div>

<div class="col-md-3">
<div class="card p-3">
<h6>Threat Level</h6>
<h2 id="threat">LOW</h2>
</div>
</div>

<div class="col-md-3">
<div class="card p-3">
<h6>Attacks Detected</h6>
<h2 id="attacks">0</h2>
</div>
</div>

<div class="col-md-3">
<div class="card p-3">
<h6>Attack Duration</h6>
<h2 id="duration">0s</h2>
</div>
</div>

<div class="col-md-3">
<div class="card p-3">
<h6>Last Attack</h6>
<h2 id="lastattack">-</h2>
</div>
</div>
</div>
</div>
</div>
<div class="card mt-4 p-3">
<h5>Traffic Trend</h5>
<canvas id="trafficChart"></canvas>
</div>
<div class="row mt-4">
<div class="col-md-4">
<div class="card p-3">
<h5>Endpoint Stats</h5>
<p>/fast : <span id="fast">0</span></p>
<p>/heavy : <span id="heavy">0</span></p>
</div>
</div>
<div class="col-md-8">
<div class="card p-3">
<h5>Recent Requests</h5>
<table class="table table-dark">
<thead>
<tr>
<th>Time</th>
<th>Method</th>
<th>Path</th>
<th>Payload</th>
<th>IP</th>
</tr>
</thead>
<tbody id="logs"></tbody>
</table>
</div>

<div class="card mt-4 p-3">
<h5>Threat Detection Logs</h5>

<table class="table table-dark">
<thead>
<tr>
<th>Time</th>
<th>Event</th>
<th>RPS</th>
</tr>
</thead>
<tbody id="alerts"></tbody>
</table>
</div>

</div>
</div>
</div>
</div>
<script>
let chart;

async function refreshDashboard(){
    const res = await fetch('/stats');
    const data = await res.json();

    document.getElementById('req').innerText = data.total_requests;
    document.getElementById('rps').innerText = data.avg_rps;
    document.getElementById('uptime').innerText = data.uptime_sec + "s";
    document.getElementById('fast').innerText = data.fast_requests;
    document.getElementById('heavy').innerText = data.heavy_requests;
    document.getElementById('cpu').innerText = data.cpu + "%";
    document.getElementById('ram').innerText = data.ram + "%";
    
    const threatBox = document.getElementById('threat');

    threatBox.innerText = data.threat_level;

    if(data.threat_level === "LOW"){
        threatBox.style.color = "#22c55e";
    }
    else if(data.threat_level === "MEDIUM"){
        threatBox.style.color = "#facc15";
    }
    else if(data.threat_level === "HIGH"){
        threatBox.style.color = "#f97316";
    }
    else{
        threatBox.style.color = "#ef4444";
    }

    document.getElementById('attacks').innerText =
    data.attack_count;

    document.getElementById('duration').innerText =
    data.attack_duration + "s";

    document.getElementById('lastattack').innerText =
    data.last_attack;

    let status = "NORMAL";
    let alertClass = "alert-success";
    let alertText = "NORMAL TRAFFIC";

    if(data.threat_level === "LOW"){
    status = "NORMAL";
    alertClass = "alert-success";
    alertText = "NORMAL TRAFFIC";
}
else if(data.threat_level === "MEDIUM"){
    status = "HIGH LOAD";
    alertClass = "alert-warning";
    alertText = "HIGH TRAFFIC DETECTED";
}
else if(data.threat_level === "HIGH"){
    status = "UNDER ATTACK";
    alertClass = "alert-danger";
    alertText = "POSSIBLE DOS ACTIVITY";
}
else{
    status = "CRITICAL";
    alertClass = "alert-danger";
    alertText = "CRITICAL DOS ATTACK DETECTED";
}

    document.getElementById('status').innerText = status;

    const alertBox = document.getElementById('alert');
    alertBox.className = "alert " + alertClass + " alert-banner";
    alertBox.innerText = alertText;

    let rows = "";
    data.logs.forEach(log => {
       rows += `
    <tr>
    <td>${log.time}</td>
    <td>${log.method}</td>
    <td>${log.path}</td>
    <td>${log.query}</td>
    <td>${log.ip}</td>
    </tr>`;
    });
    document.getElementById('logs').innerHTML = rows;

    let attackRows = "";

data.alerts.forEach(alert => {
    attackRows += `
    <tr>
        <td>${alert.time}</td>
        <td>${alert.event}</td>
        <td>${alert.rps}</td>
    </tr>`;
});

document.getElementById('alerts').innerHTML = attackRows;


    const labels = data.traffic.map(x => x.time);
    const values = data.traffic.map(x => x.rps);

    if(!chart){
        chart = new Chart(
            document.getElementById('trafficChart'),
            {
                type:'line',
                data:{
                    labels:labels,
                    datasets:[{
                        label:'RPS',
                        data:values,
                        borderColor:'#00d4ff',
                        backgroundColor:'rgba(0,212,255,0.2)',
                        fill:true,
                        borderWidth:3,
                        pointRadius:3,
                        tension:0.4
                    }]
                },
                options:{
                    responsive:true,
                    animation:false,
                    plugins:{
                        legend:{
                            labels:{color:'white'}
                        }
                    },
                    scales:{
                        x:{
                            ticks:{color:'white'},
                            grid:{color:'rgba(255,255,255,0.08)'}
                        },
                        y:{
                            beginAtZero:true,
                            ticks:{color:'white'},
                            grid:{color:'rgba(255,255,255,0.08)'}
                        }
                    }
                }
            }
        );
    }else{
        chart.data.labels = labels;
        chart.data.datasets[0].data = values;
        chart.update();
    }
}

refreshDashboard();
setInterval(refreshDashboard, 1000);
</script>
</body>
</html>
"""


@app.route("/fast")
def fast():
    global _fast_count
    with _counter_lock:
        _fast_count += 1
        current_req = _request_count

    return jsonify({
        "status": "ok",
        "request_no": current_req,  
        "ts": time.time()
    })


@app.route("/heavy")
def heavy():
    """Endpoint berat — komputasi CPU intensif + sleep, mensimulasikan query DB lambat."""
    global _heavy_count
    with _counter_lock:
        _heavy_count += 1
        current_req = _request_count

    # Ambil parameter delay (dalam detik), default 0.5, max 5 detik
    delay = float(request.args.get("delay", 0.5))
    delay = min(delay, 5.0)

    # Faktor komputasi (default 1, max 5) — mengontrol seberapa berat komputasi
    factor = float(request.args.get("factor", 1))
    factor = min(factor, 5)

    # Simulasi komputasi berat: hitung bilangan prima hingga n
    # n bisa sampai 50,000 tergantung factor
    n = int(10_000 * factor)

    primes = []
    for i in range(2, n):
        prime = True
        limit = int(math.sqrt(i)) + 1
        for j in range(2, limit):
            if i % j == 0:
                prime = False
                break
        if prime:
            primes.append(i)

    # Sleep untuk mensimulasikan I/O blocking (query DB lambat)
    time.sleep(delay)

    return jsonify({
        "status": "done",
        "primes_count": len(primes),
        "request_no": current_req,
        "delay": delay,
        "factor": factor,
        "n_max": n
    })


@app.route("/stats")
def stats():

    global _last_count
    global _rps_history

    global _attack_count
    global _last_attack_time
    global _attack_active
    global _attack_started

    uptime = max(time.time() - _start_time, 1)

    with _counter_lock: 
        current_count = _request_count
        fc = _fast_count
        hc = _heavy_count

    current_rps = current_count - _last_count
    _last_count = current_count

    _rps_samples.append(current_rps)

    avg_rps = round(
        sum(_rps_samples) / len(_rps_samples),
        1
    )

    _rps_history.append({
        "time": time.strftime("%H:%M:%S"),
        "rps": avg_rps
    })

    if current_rps > 80:

        _last_attack_time = time.time()

        if not _attack_active:

            _attack_active = True
            _attack_count += 1
            _attack_started = time.time()

            _attack_history.append({
                "time": time.strftime("%H:%M:%S"),
                "event": "Possible DoS Activity",
                "rps": avg_rps
            })

    if time.time() - _last_attack_time < 10:

        attack_state = True

    else:

        attack_state = False

        if _attack_active:

            _attack_active = False

            _attack_history.append({
                "time": time.strftime("%H:%M:%S"),
                "event": "Attack Ended",
                "rps": avg_rps
            })
    
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    if current_rps < 15:
        threat_level = "LOW"
    elif current_rps < 50:
        threat_level = "MEDIUM"
    elif current_rps < 120:
        threat_level = "HIGH"
    else:
        threat_level = "CRITICAL"

    attack_duration = 0

    if attack_state and _attack_started:
        attack_duration = round(
        time.time() - _attack_started,
        1
    )
    else:
        attack_duration = 0

    return jsonify({
        "total_requests": current_count,
        "uptime_sec": round(uptime, 1),
        "avg_rps": avg_rps,
        "cpu": cpu,
        "ram": ram,
        "fast_requests": fc,
        "heavy_requests": hc,
        "logs": list(_request_log)[-10:],
        "traffic": list(_rps_history),
        "attack_active": attack_state,
        "attack_count": _attack_count,
        "threat_level": threat_level,
        "attack_duration": attack_duration,
        "last_attack":
        time.strftime(
        "%H:%M:%S",
        time.localtime(_last_attack_time)
) if _last_attack_time else "-",

"alerts": list(_attack_history) 
    })


if __name__ == "__main__":
    print("=" * 55)
    print("  [LAB] DoS Target Website")
    print("  URL    : http://localhost:5004")
    print("  HANYA untuk edukasi di lingkungan lab lokal!")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5004, debug=False, threaded=True)  