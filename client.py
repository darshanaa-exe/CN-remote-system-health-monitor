import argparse
import json
import platform
import socket
import time

import psutil

from config import SEND_INTERVAL
from security import encrypt_message


def parse_args():
    parser = argparse.ArgumentParser(description="Remote Health Monitoring Client")
    parser.add_argument("node_id", help="Unique node identifier, for example node-1")
    parser.add_argument("--server-ip", default="127.0.0.1", help="Server IP address")
    parser.add_argument("--port", type=int, default=9999, help="Server UDP port")
    parser.add_argument("--interval", type=float, default=SEND_INTERVAL, help="Send interval in seconds")
    return parser.parse_args()


def main():
    args = parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = platform.node() or "unknown-host"

    print("=" * 70)
    print(f"Remote Health Monitoring Client :: {args.node_id}")
    print(f"Server   : {args.server_ip}:{args.port}")
    print(f"Interval : {args.interval:.1f}s")
    print("Protocol : UDP + JSON payload + application-layer encryption")
    print("=" * 70)

    try:
        while True:
            payload = {
                "node_id": args.node_id,
                "hostname": hostname,
                "cpu": psutil.cpu_percent(interval=1),
                "mem": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent,
            }

            encrypted = encrypt_message(json.dumps(payload))
            sock.sendto(encrypted, (args.server_ip, args.port))

            print(
                f"[SENT] {payload['node_id']} | "
                f"CPU={payload['cpu']:.1f}% MEM={payload['mem']:.1f}% DISK={payload['disk']:.1f}%"
            )

            # cpu_percent already consumed ~1 second, so sleep the remaining interval if possible
            remaining = max(0.0, args.interval - 1.0)
            time.sleep(remaining)

    except KeyboardInterrupt:
        print("\n[INFO] Client shutting down.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
