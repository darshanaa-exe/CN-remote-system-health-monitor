# Remote Health Monitoring with Web Dashboard

This project monitors CPU, memory, and disk usage from multiple clients over UDP and displays the results on a live web dashboard.

## Features
- UDP socket based monitoring
- Encrypted packet transfer using Fernet
- Multi-client support
- Threshold-based alerts
- Offline node detection
- Summary cards
- Search and status filter
- Selected node trend chart
- Node comparison chart
- Recent alerts panel
- Recent packet history

## Files
- `client.py` - client that collects metrics and sends packets
- `server.py` - UDP receiver + Flask web dashboard
- `config.py` - configuration values
- `security.py` - shared encryption helpers
- `templates/index.html` - dashboard page
- `static/style.css` - dashboard styling

## Install
```bash
pip install psutil cryptography flask
```

## Run
Start the server first:
```bash
python server.py
```

Open the dashboard:
```text
http://127.0.0.1:5000
```

Run clients in separate terminals:
```bash
python client.py node-1 --server-ip 127.0.0.1 --port 9999
python client.py node-2 --server-ip 127.0.0.1 --port 9999
python client.py node-3 --server-ip 127.0.0.1 --port 9999
```

## How offline works
A node becomes offline if the server does not receive a packet from that node for more than `OFFLINE_TIMEOUT` seconds.

## Viva explanation
The UDP socket layer is the core monitoring system. The web dashboard is only the visualization layer on top of the aggregation server.
