# Remote System Health Monitoring Service
**CN Mini Project – Topic 23 | Protocol: UDP | Language: Python**

---

## Overview
A secure, multi-client system health monitoring service where remote nodes (clients)
periodically collect CPU, memory, and disk metrics and transmit them over **encrypted
UDP packets** to a central aggregation server. The server decrypts, analyzes, and
displays live metrics with threshold-based alerts.

---

## Security Approach
Python's built-in `ssl` module does not support **DTLS** (Datagram TLS — the TLS
equivalent for UDP). To satisfy the security requirement while keeping UDP as the
transport protocol, **Fernet symmetric encryption** is used at the application layer.

Fernet provides:
- **AES-128-CBC** encryption for confidentiality
- **HMAC-SHA256** authentication to detect tampering
- Any modified or forged packet is automatically rejected by the server

---

## Architecture
```
 ┌─────────────┐      Encrypted UDP packet      ┌──────────────────────────┐
 │  Node A     │ ────────────────────────────▶  │                          │
 │  client.py  │                                │   Central Server         │
 └─────────────┘                                │   server.py              │
                                                │                          │
 ┌─────────────┐      Encrypted UDP packet      │  • Decrypts packets      │
 │  Node B     │ ────────────────────────────▶  │  • Aggregates metrics    │
 │  client.py  │                                │  • Checks thresholds     │
 └─────────────┘                                │  • Generates alerts      │
                                                │  • One thread/packet     │
 ┌─────────────┐                                └──────────────────────────┘
 │  load_test  │ ── 20 simulated UDP clients ─▶  (performance testing)
 └─────────────┘
```

---

## Files
| File | Description |
|------|-------------|
| `server.py` | Central server — UDP socket, decrypt, aggregate, alert |
| `client.py` | Monitoring node — collects real metrics, encrypts, sends via UDP |
| `security.py` | Fernet encryption/decryption (application-layer security) |
| `config.py` | Shared configuration — IP, port, thresholds, interval |
| `load_test.py` | Simulates 20 concurrent encrypted UDP clients |

---

## Setup & Usage

### Step 1 — Install dependencies
```bash
pip install psutil cryptography
```

### Step 2 — Start the server
```bash
python server.py
```

### Step 3 — Start one or more clients (separate terminals)
```bash
python client.py
```

### Step 4 — Run load test (performance evaluation)
```bash
python load_test.py
```

---

## Configuration (`config.py`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `SERVER_IP` | `127.0.0.1` | Server IP address |
| `SERVER_PORT` | `9999` | UDP port |
| `CPU_THRESHOLD` | `80` | Alert if CPU % exceeds this |
| `MEM_THRESHOLD` | `90` | Alert if Memory % exceeds this |
| `DISK_THRESHOLD` | `90` | Alert if Disk % exceeds this |
| `SEND_INTERVAL` | `5` | Seconds between metric reports |

---

## Metrics Collected
- **CPU Usage** (%) via `psutil.cpu_percent()`
- **Memory Usage** (%) via `psutil.virtual_memory().percent`
- **Disk Usage** (%) via `psutil.disk_usage('/').percent`
