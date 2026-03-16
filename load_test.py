import socket
import random
import time
import threading
from config import *
from security import encrypt_message

print("=" * 55)
print("  Load Test — 20 concurrent encrypted UDP clients")
print("=" * 55 + "\n")

# ── Lock for clean console output ─────────────────────────────────────────────
print_lock = threading.Lock()

def simulate_client(node: str):
    """Simulate one monitoring node sending encrypted UDP packets."""
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        try:
            cpu  = random.randint(10, 95)
            mem  = random.randint(20, 95)
            disk = random.randint(10, 95)

            message   = f"{node}|{cpu}|{mem}|{disk}"
            encrypted = encrypt_message(message)

            client.sendto(encrypted, (SERVER_IP, SERVER_PORT))

            with print_lock:
                print(f"[{node}] Sent: {message}")

            time.sleep(2)

        except Exception as e:
            with print_lock:
                print(f"[{node}] Error: {e}")
            time.sleep(3)

# ── Launch 20 simulated client threads ────────────────────────────────────────
threads = []
for i in range(20):
    node = f"SIM_NODE_{i:02d}"
    t = threading.Thread(target=simulate_client, args=(node,), daemon=True)
    t.start()
    threads.append(t)
    time.sleep(0.1)   # slight stagger to avoid thundering herd

print(f"[INFO] {len(threads)} simulated clients running. Press Ctrl+C to stop.\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[INFO] Load test stopped.")
