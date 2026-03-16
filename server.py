import socket
import threading
from datetime import datetime
from config import *
from security import decrypt_message

# ── UDP Socket setup ───────────────────────────────────────────────────────────
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP, SERVER_PORT))

print("=" * 75)
print("  Remote Health Monitoring Server  (UDP + Application-Layer Encryption)")
print(f"  Listening on {SERVER_IP}:{SERVER_PORT}")
print("=" * 75)

print("\n{:<12} {:<15} {:<8} {:<10} {:<8} {:<10} {:<10}".format(
    "NODE", "IP", "CPU", "MEMORY", "DISK", "TIME", "STATUS"
))
print("-" * 80)

# ── Lock to prevent garbled output from concurrent prints ─────────────────────
print_lock = threading.Lock()

def handle_packet(data: bytes, addr: tuple):
    """Decrypt and process one incoming UDP packet."""
    try:
        message = decrypt_message(data)

        parts = message.split("|")
        if len(parts) != 4:
            with print_lock:
                print(f"[WARN] Malformed packet from {addr[0]}: {message}")
            return

        node, cpu_s, mem_s, disk_s = parts

        try:
            cpu  = float(cpu_s)
            mem  = float(mem_s)
            disk = float(disk_s)
        except ValueError:
            with print_lock:
                print(f"[WARN] Non-numeric metrics from {addr[0]}: {message}")
            return

        # ── Threshold alert logic ──────────────────────────────────────────────
        alerts = []
        if cpu  > CPU_THRESHOLD:  alerts.append("CPU ALERT")
        if mem  > MEM_THRESHOLD:  alerts.append("MEM ALERT")
        if disk > DISK_THRESHOLD: alerts.append("DISK ALERT")
        status = " | ".join(alerts) if alerts else "OK"

        timestamp = datetime.now().strftime("%H:%M:%S")

        with print_lock:
            print("{:<12} {:<15} {:<8} {:<10} {:<8} {:<10} {:<10}".format(
                node,
                addr[0],
                f"{cpu}%",
                f"{mem}%",
                f"{disk}%",
                timestamp,
                status
            ))

    except Exception:
        with print_lock:
            print(f"[WARN] Invalid or tampered packet from {addr[0]} — dropped")

# ── Main receive loop ──────────────────────────────────────────────────────────
print("[INFO] Waiting for encrypted UDP packets...\n")
while True:
    try:
        # Buffer size 4096 — required for Fernet encrypted payloads
        data, addr = server.recvfrom(4096)

        # Handle each packet in its own thread so the receive loop never blocks
        t = threading.Thread(target=handle_packet, args=(data, addr), daemon=True)
        t.start()

    except KeyboardInterrupt:
        print("\n[INFO] Server shutting down.")
        break
    except Exception as e:
        print(f"[ERROR] {e}")
