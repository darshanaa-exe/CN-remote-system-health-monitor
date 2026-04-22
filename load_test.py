import argparse
import json
import random
import socket
import threading
import time

from security import encrypt_message


def parse_args():
    parser = argparse.ArgumentParser(
        description="UDP load test for Remote Health Monitoring server"
    )
    parser.add_argument("--server-ip", required=True, help="Target server IP address")
    parser.add_argument("--port", type=int, default=9999, help="Target UDP port")
    parser.add_argument("--clients", type=int, default=50, help="Number of simulated clients")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between packets from each simulated client",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=20,
        help="How many packets each simulated client should send",
    )
    parser.add_argument(
        "--startup-spread",
        type=float,
        default=1.5,
        help="Random spread in seconds before clients begin sending",
    )
    return parser.parse_args()


def build_payload(node_id: str) -> dict:
    """Create a realistic random payload for one simulated node."""
    return {
        "node_id": node_id,
        "hostname": f"loadtest-{node_id}",
        "cpu": round(random.uniform(5, 95), 1),
        "mem": round(random.uniform(20, 95), 1),
        "disk": round(random.uniform(10, 98), 1),
    }


def client_worker(node_id: str, server_ip: str, port: int, interval: float, rounds: int, startup_spread: float):
    """Simulate one client sending multiple encrypted UDP packets."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        if startup_spread > 0:
            time.sleep(random.uniform(0, startup_spread))

        for sequence in range(1, rounds + 1):
            payload = build_payload(node_id)
            payload["sequence"] = sequence
            payload["sent_at"] = time.time()

            encrypted = encrypt_message(json.dumps(payload))
            sock.sendto(encrypted, (server_ip, port))

            print(
                f"[{node_id}] sent packet {sequence}/{rounds} "
                f"(CPU={payload['cpu']} MEM={payload['mem']} DISK={payload['disk']})"
            )

            if sequence < rounds:
                time.sleep(interval)
    finally:
        sock.close()


def main():
    args = parse_args()

    print("=" * 72)
    print("Remote Health Monitoring :: UDP Load Test")
    print(f"Target server : {args.server_ip}:{args.port}")
    print(f"Simulated clients : {args.clients}")
    print(f"Packets per client : {args.rounds}")
    print(f"Interval per client : {args.interval:.2f}s")
    print("=" * 72)

    start_time = time.time()
    threads = []

    for i in range(1, args.clients + 1):
        node_id = f"stress-node-{i}"
        t = threading.Thread(
            target=client_worker,
            args=(node_id, args.server_ip, args.port, args.interval, args.rounds, args.startup_spread),
            daemon=False,
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = max(time.time() - start_time, 1e-9)
    total_packets = args.clients * args.rounds
    throughput = total_packets / elapsed

    print("\n" + "=" * 72)
    print("Load test complete")
    print(f"Total packets attempted : {total_packets}")
    print(f"Total time taken        : {elapsed:.2f}s")
    print(f"Approx. send throughput : {throughput:.2f} packets/sec")
    print("=" * 72)


if __name__ == "__main__":
    main()
