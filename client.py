import socket
import psutil
import time
import random
from config import *
from security import encrypt_message

# ── UDP Socket setup ───────────────────────────────────────────────────────────
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

node_id = "NODE_" + str(random.randint(1, 100))

print("=" * 50)
print(f"  Remote Health Monitoring Client — {node_id}")
print(f"  Sending to {SERVER_IP}:{SERVER_PORT} every {SEND_INTERVAL}s")
print("  Security: Fernet AES-128-CBC + HMAC-SHA256")
print("=" * 50 + "\n")

while True:
    try:
        # ── Collect real system metrics ────────────────────────────────────────
        cpu  = psutil.cpu_percent(interval=1)
        mem  = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        message = f"{node_id}|{cpu}|{mem}|{disk}"

        # ── Encrypt and send ───────────────────────────────────────────────────
        encrypted = encrypt_message(message)

        client.sendto(encrypted, (SERVER_IP, SERVER_PORT))

        print(f"[SENT] {message}  →  encrypted ({len(encrypted)} bytes)")

        time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("\n[INFO] Client shutting down.")
        client.close()
        break
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(2)
