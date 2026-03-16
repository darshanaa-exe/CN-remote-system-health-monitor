from cryptography.fernet import Fernet

# Application-layer security using Fernet symmetric encryption.
# This is used because Python's built-in ssl module does not support
# DTLS (Datagram TLS), which is the TLS equivalent for UDP sockets.
# Fernet provides AES-128-CBC encryption + HMAC-SHA256 authentication,
# ensuring both confidentiality and integrity of all transmitted packets.

# Shared pre-distributed secret key (both server and clients must have this)
KEY = b'uFLZrlP7FDwvWLgcJqGnaMtP1hWt2Bpdc83zgmxcwbo='

cipher = Fernet(KEY)

def encrypt_message(message: str) -> bytes:
    """Encrypt a plaintext string into an encrypted byte payload."""
    return cipher.encrypt(message.encode())

def decrypt_message(encrypted: bytes) -> str:
    """Decrypt an encrypted byte payload back to a plaintext string.
    Raises cryptography.fernet.InvalidToken if the data is tampered."""
    return cipher.decrypt(encrypted).decode()
