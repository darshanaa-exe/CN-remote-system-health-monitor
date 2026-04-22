# Remote System Health Monitoring Service

COMPUTER NETWORKS - Socket Programming – Jackfruit Mini Project

NAME: DARSHANA S     SRN: PES1UG24CS913  <br>
NAME: PRASHANT       SRN: PES1UG24CS597   <br>
NAME: PRAVEEN        SRN: PES1UG24CS832  <br>
 	  

A UDP-based multi-client system health monitoring solution with encrypted packet transfer and a live web dashboard. Built as part of the CN (Computer Networks) Socket Programming Mini Project.

---

## Overview

This project implements a **Remote System Health Monitoring Service** where multiple client nodes periodically collect and transmit system metrics (CPU, memory, disk usage) to a central aggregation server over UDP. The server processes incoming data in real time, evaluates thresholds, raises alerts, and exposes a live web dashboard for visualization.

### Key Features

- **UDP socket-based communication** between clients and server
- **Application-layer encryption** using Fernet symmetric encryption (shared key)
- **Multi-client support** — handles any number of concurrent nodes via threading
- **Threshold-based alerting** for CPU, memory, and disk usage
- **Offline detection** — nodes not heard from within a timeout window are marked offline
- **Live web dashboard** (Flask + vanilla JS) with auto-refresh every 2 seconds
- **Load testing tool** to simulate up to N concurrent clients under configurable load
- **Node trend charts** and comparison bar charts rendered on HTML5 Canvas

---

## Architecture

```
┌─────────────────────┐        UDP (Encrypted)        ┌──────────────────────────────┐
│   Client Node(s)    │ ───────────────────────────►  │         UDP Server           │
│                     │                               │  (Threaded packet handler)   │
│  - psutil metrics   │                               │  - Decrypt & parse payload   │
│  - JSON payload     │                               │  - Evaluate thresholds       │
│  - Fernet encrypt   │                               │  - Store node state          │
└─────────────────────┘                               └──────────────┬───────────────┘
                                                                      │
                                                              Flask REST API
                                                                      │
                                                       ┌──────────────▼───────────────┐
                                                       │       Web Dashboard          │
                                                       │  - Node status table         │
                                                       │  - Alert feed                │
                                                       │  - Comparison bar chart      │
                                                       │  - Packet history table      │
                                                       └──────────────────────────────┘
```

**Communication Flow:**
1. Each client collects CPU, memory, and disk metrics using `psutil`
2. Metrics are JSON-serialized and encrypted with Fernet before transmission
3. The server receives UDP datagrams and spawns a handler thread per packet
4. Each handler decrypts, parses, and stores the payload; alerts are triggered if thresholds are exceeded
5. The Flask web server exposes `/api/dashboard` and `/api/trends/<node_id>` endpoints
6. The browser polls these endpoints every 2 seconds and updates the dashboard

---

## Project Structure

```
.
├── server.py          # UDP receiver + Flask web server
├── client.py          # Health monitoring client (real metrics via psutil)
├── load_test.py       # Simulated multi-client load tester
├── security.py        # Fernet encryption/decryption helpers
├── config.py          # Shared configuration constants
├── templates/
│   └── index.html     # Web dashboard (HTML + JS)
└── static/
    └── style.css      # Dashboard styling
```

---

## Configuration (`config.py`)

| Parameter             | Default     | Description                                        |
|-----------------------|-------------|----------------------------------------------------|
| `SERVER_IP`           | `0.0.0.0`   | UDP server bind address                            |
| `SERVER_PORT`         | `9999`      | UDP server port                                    |
| `WEB_HOST`            | `127.0.0.1` | Flask web server host                              |
| `WEB_PORT`            | `5000`      | Flask web server port                              |
| `CPU_THRESHOLD`       | `80.0`      | CPU % above which an alert is raised               |
| `MEM_THRESHOLD`       | `70.0`      | Memory % above which an alert is raised            |
| `DISK_THRESHOLD`      | `90.0`      | Disk % above which an alert is raised              |
| `SEND_INTERVAL`       | `5.0`       | Seconds between client transmissions               |
| `OFFLINE_TIMEOUT`     | `15.0`      | Seconds of silence before a node is marked offline |
| `MAX_RECENT_HISTORY`  | `120`       | Max packets kept in the recent history buffer      |
| `MAX_ALERT_HISTORY`   | `60`        | Max alerts kept in the alert buffer                |
| `MAX_TREND_POINTS`    | `40`        | Max trend data points stored per node              |

---

## Setup

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install flask psutil cryptography
```

> **Note:** `psutil` is only required on machines running `client.py`. The server and load tester do not need it.

---

## Running the System

### 1. Start the Server

```bash
python server.py
```

The server begins listening for UDP packets on port `9999` and serves the web dashboard at [http://127.0.0.1:5000](http://127.0.0.1:5000).

### 2. Start a Client Node

```bash
python client.py <node_id> --server-ip <SERVER_IP>
```

**Examples:**

```bash
# Client on the same machine
python client.py node-1 --server-ip 127.0.0.1

# Client pointing to a remote server
python client.py node-2 --server-ip 192.168.1.100 --port 9999 --interval 3
```

**Client arguments:**

| Argument      | Default      | Description                             |
|---------------|--------------|-----------------------------------------|
| `node_id`     | *(required)* | Unique name for this node               |
| `--server-ip` | `127.0.0.1`  | IP address of the server                |
| `--port`      | `9999`       | UDP port of the server                  |
| `--interval`  | `5.0`        | Seconds between metric transmissions    |

### 3. Open the Dashboard

Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. The dashboard auto-refreshes every 2 seconds.

---

## Load Testing

The `load_test.py` script simulates multiple concurrent clients to evaluate server performance under stress.

```bash
python load_test.py --server-ip 127.0.0.1 --clients 50 --rounds 20 --interval 1.0
```

**Arguments:**

| Argument           | Default      | Description                                            |
|--------------------|--------------|--------------------------------------------------------|
| `--server-ip`      | *(required)* | Target server IP address                               |
| `--port`           | `9999`       | Target UDP port                                        |
| `--clients`        | `50`         | Number of simulated concurrent client nodes            |
| `--interval`       | `1.0`        | Seconds between packets from each simulated client     |
| `--rounds`         | `20`         | Number of packets each simulated client sends          |
| `--startup-spread` | `1.5`        | Random delay spread (seconds) before clients start     |

**Example — heavy load test:**
```bash
python load_test.py --server-ip 127.0.0.1 --clients 100 --rounds 30 --interval 0.5
```

At the end of the run, the script reports total packets sent, elapsed time, and approximate send throughput (packets/sec).

---

## Security

Encryption is handled in `security.py` using the **Fernet** symmetric encryption scheme from the `cryptography` library.

- A shared 32-byte base64-encoded key is used by both clients and the server
- Every UDP datagram is fully encrypted before transmission
- The server silently drops any packet that fails decryption (counted as `invalid_packets` in the dashboard stats)

> **Note for production use:** The shared key is currently hardcoded in `security.py`. For deployment, load it from an environment variable or a secrets manager and never commit it to version control.

---

## API Endpoints

| Endpoint                | Method | Description                                                    |
|-------------------------|--------|----------------------------------------------------------------|
| `/`                     | GET    | Serves the live web dashboard                                  |
| `/api/dashboard`        | GET    | Returns full dashboard JSON (summary, nodes, alerts, history)  |
| `/api/trends/<node_id>` | GET    | Returns time-series trend data for a specific node             |

### Sample `/api/dashboard` Response

```json
{
  "summary": {
    "total_nodes": 3,
    "online_nodes": 2,
    "offline_nodes": 1,
    "active_alerts": 1,
    "total_packets": 472,
    "invalid_packets": 0,
    "uptime_seconds": 320
  },
  "nodes": [...],
  "alerts": [...],
  "history": [...]
}
```

---

## Dashboard Features

- **Summary cards** — total/online/offline nodes, active alerts, total packet count
- **Node Status table** — live snapshot of every node with CPU/MEM/DISK percentages and status badges; supports search and status filtering
- **Recent Alerts feed** — latest threshold violations with node name, violated metrics, and timestamp
- **Node Comparison chart** — grouped bar chart comparing CPU, memory, and disk across all active nodes
- **Packet History table** — last 20 packets received by the server in reverse chronological order

---

## Performance Notes

Under load testing with 50 concurrent simulated clients at 1-second intervals:
- The threaded UDP receiver handles each incoming datagram in its own daemon thread
- Flask serves dashboard API requests independently on a separate thread pool
- A shared `threading.Lock` protects all in-memory data structures from race conditions
- Packets that fail decryption are dropped and tracked without crashing the receiver loop

---

## Evaluation Criteria Mapping

| Criterion                         | Implementation                                                              |
|-----------------------------------|-----------------------------------------------------------------------------|
| Problem Definition & Architecture | UDP client-server, multi-client support, threaded server, REST dashboard    |
| Core Socket Implementation        | Raw `socket.SOCK_DGRAM`; explicit `bind`, `sendto`, `recvfrom`              |
| Feature Implementation            | Metrics collection, multi-client aggregation, Fernet encryption, alerting   |
| Performance Evaluation            | `load_test.py` with configurable clients, rounds, intervals; throughput reporting |
| Optimization & Fixes              | Offline detection, invalid packet handling, thread-safe state management    |
| Final Demo / GitHub               | Full source, README, and setup instructions in this repository              |
