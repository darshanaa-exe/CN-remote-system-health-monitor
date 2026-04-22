import json
import socket
import threading
import time
from collections import deque
from copy import deepcopy
from datetime import datetime

from flask import Flask, jsonify, render_template

from config import (
    CPU_THRESHOLD,
    DISK_THRESHOLD,
    MAX_ALERT_HISTORY,
    MAX_RECENT_HISTORY,
    MAX_TREND_POINTS,
    MEM_THRESHOLD,
    OFFLINE_TIMEOUT,
    SERVER_IP,
    SERVER_PORT,
    WEB_HOST,
    WEB_PORT,
)
from security import decrypt_message


app = Flask(__name__)

data_lock = threading.Lock()
latest_nodes = {}
recent_packets = deque(maxlen=MAX_RECENT_HISTORY)
recent_alerts = deque(maxlen=MAX_ALERT_HISTORY)
node_trends = {}
stats = {
    "total_packets": 0,
    "invalid_packets": 0,
    "total_alerts": 0,
    "start_time": time.time(),
}


def now_str():
    return datetime.now().strftime("%H:%M:%S")


def evaluate_status(cpu: float, mem: float, disk: float) -> str:
    alerts = []
    if cpu > CPU_THRESHOLD:
        alerts.append("CPU ALERT")
    if mem > MEM_THRESHOLD:
        alerts.append("MEM ALERT")
    if disk > DISK_THRESHOLD:
        alerts.append("DISK ALERT")
    return " | ".join(alerts) if alerts else "OK"


def udp_receiver():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((SERVER_IP, SERVER_PORT))

    print("=" * 110)
    print("Remote Health Monitoring Server :: UDP Receiver + Web Dashboard")
    print(f"UDP Listening : {SERVER_IP}:{SERVER_PORT}")
    print(f"Web Dashboard : http://{WEB_HOST}:{WEB_PORT}")
    print("=" * 110)
    print("{:<12} {:<15} {:<20} {:<8} {:<8} {:<8} {:<18} {:<10}".format(
        "NODE", "IP", "HOSTNAME", "CPU", "MEM", "DISK", "STATUS", "TIME"
    ))
    print("-" * 110)

    while True:
        try:
            packet, addr = server.recvfrom(4096)
            threading.Thread(target=handle_packet, args=(packet, addr), daemon=True).start()
        except Exception as exc:
            print(f"[ERROR] UDP receive failed: {exc}")


def handle_packet(packet: bytes, addr):
    received_at = time.time()
    time_label = datetime.fromtimestamp(received_at).strftime("%H:%M:%S")

    try:
        message = decrypt_message(packet)
        payload = json.loads(message)

        node_id = str(payload.get("node_id", "unknown"))
        hostname = str(payload.get("hostname", "unknown"))
        cpu = float(payload.get("cpu", 0.0))
        mem = float(payload.get("mem", 0.0))
        disk = float(payload.get("disk", 0.0))

        status = evaluate_status(cpu, mem, disk)

        record = {
            "node_id": node_id,
            "ip": addr[0],
            "hostname": hostname,
            "cpu": cpu,
            "mem": mem,
            "disk": disk,
            "status": status,
            "time": time_label,
            "last_seen_epoch": received_at,
        }

        with data_lock:
            stats["total_packets"] += 1
            latest_nodes[node_id] = record

            recent_packets.append(record)

            trend = node_trends.setdefault(node_id, deque(maxlen=MAX_TREND_POINTS))
            trend.append({
                "time": time_label,
                "cpu": cpu,
                "mem": mem,
                "disk": disk,
            })

            if "ALERT" in status:
                recent_alerts.appendleft(record)
                stats["total_alerts"] += 1

        print("{:<12} {:<15} {:<20} {:<8} {:<8} {:<8} {:<18} {:<10}".format(
            node_id,
            addr[0],
            hostname[:20],
            f"{cpu:.1f}%",
            f"{mem:.1f}%",
            f"{disk:.1f}%",
            status[:18],
            time_label,
        ))

    except Exception:
        with data_lock:
            stats["invalid_packets"] += 1
        print("{:<12} {:<15} {:<20} {:<8} {:<8} {:<8} {:<18} {:<10}".format(
            "INVALID",
            addr[0],
            "-",
            "-",
            "-",
            "-",
            "DROPPED",
            time_label,
        ))


def build_nodes_snapshot():
    current = time.time()
    snapshot = []

    with data_lock:
        for node_id, record in latest_nodes.items():
            item = deepcopy(record)
            age = current - item["last_seen_epoch"]
            item["is_offline"] = age > OFFLINE_TIMEOUT
            item["seconds_since_seen"] = round(age, 1)
            if item["is_offline"]:
                item["status"] = "OFFLINE"
            snapshot.append(item)

    snapshot.sort(key=lambda x: x["node_id"].lower())
    return snapshot


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dashboard")
def api_dashboard():
    nodes = build_nodes_snapshot()

    online = sum(1 for n in nodes if not n["is_offline"])
    offline = sum(1 for n in nodes if n["is_offline"])
    active_alerts = sum(1 for n in nodes if ("ALERT" in n["status"]))

    with data_lock:
        uptime_seconds = int(time.time() - stats["start_time"])
        response = {
            "summary": {
                "total_nodes": len(nodes),
                "online_nodes": online,
                "offline_nodes": offline,
                "active_alerts": active_alerts,
                "total_packets": stats["total_packets"],
                "invalid_packets": stats["invalid_packets"],
                "uptime_seconds": uptime_seconds,
            },
            "nodes": nodes,
            "alerts": list(recent_alerts)[:12],
            "history": list(recent_packets)[-20:],
        }
    return jsonify(response)


@app.route("/api/trends/<node_id>")
def api_trends(node_id):
    with data_lock:
        trend = list(node_trends.get(node_id, []))
    return jsonify(trend)


def main():
    udp_thread = threading.Thread(target=udp_receiver, daemon=True)
    udp_thread.start()

    app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
